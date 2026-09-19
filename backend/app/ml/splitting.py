"""Chronological Time-Aware and Event-Aware Data Splitter for Leakage-Safe Model Training.

Implements the official SIH26079 Splitting & Leakage Protocol (§8.3, §10.4):
- Chronological temporal splitting: max(train) <= min(val) <= max(val) <= min(test)
- Event grouping: all leads and records from a cyclone/monsoon episode are kept in ONE split
- Temporal embargo/purge windows between partitions (e.g., 14-day or 21-day embargo)
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from backend.app.data.training_dataset import HistoricalTrainingRow


class TemporalLeakageError(ValueError):
    """Raised when temporal train/validation/test partitions overlap or violate causality."""


class EventLeakageError(ValueError):
    """Raised when records belonging to the same weather event/episode span multiple partitions."""


@dataclass
class DatasetSplits:
    """Container holding chronological and event-safe data partitions."""

    train_rows: list[HistoricalTrainingRow]
    val_rows: list[HistoricalTrainingRow]
    test_rows: list[HistoricalTrainingRow]
    train_time_range: tuple[str, str]
    val_time_range: tuple[str, str]
    test_time_range: tuple[str, str]
    held_out_events: list[str] = field(default_factory=list)
    purged_rows_count: int = 0


class TemporalDataSplitter:
    """Partitions historical verification records strictly by chronological issue timestamp."""

    def __init__(
        self,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        embargo_days: int = 0,
    ):
        if not abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5:
            raise ValueError(f"Ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}")
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.embargo_days = embargo_days

    @staticmethod
    def _parse_iso(iso_str: str) -> datetime:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    def split(self, rows: list[HistoricalTrainingRow]) -> DatasetSplits:
        """Split rows chronologically into Train, Validation, and Test partitions.

        Strict Scientific Rule:
        max(train.issue_time) <= min(val.issue_time) <= max(val.issue_time) <= min(test.issue_time)
        """
        if len(rows) < 3:
            raise ValueError(f"Need at least 3 rows for temporal train/val/test split, got {len(rows)}")

        # Sort chronologically by issue_time first, then valid_time
        sorted_rows = sorted(
            rows,
            key=lambda r: (self._parse_iso(r.issue_time), self._parse_iso(r.valid_time)),
        )

        n = len(sorted_rows)
        n_train = max(1, int(n * self.train_ratio))
        n_val = max(1, int(n * self.val_ratio))

        # Adjust for boundary allocations
        if n_train + n_val >= n:
            n_train = max(1, n - 2)
            n_val = 1

        train = sorted_rows[:n_train]
        val = sorted_rows[n_train : n_train + n_val]
        test = sorted_rows[n_train + n_val :]

        if not test:
            test = [val.pop()] if len(val) > 1 else [train.pop()]

        # Apply embargo if configured
        purged_count = 0
        if self.embargo_days > 0:
            embargo_delta = timedelta(days=self.embargo_days)
            train_cutoff = self._parse_iso(train[-1].issue_time)
            # Purge val rows within embargo of train
            initial_val_len = len(val)
            val = [r for r in val if (self._parse_iso(r.issue_time) - train_cutoff) >= embargo_delta]
            purged_count += (initial_val_len - len(val))

            if val:
                val_cutoff = self._parse_iso(val[-1].issue_time)
                initial_test_len = len(test)
                test = [r for r in test if (self._parse_iso(r.issue_time) - val_cutoff) >= embargo_delta]
                purged_count += (initial_test_len - len(test))

        # Verify temporal boundaries
        if not train or not val or not test:
            raise ValueError("Partitioning resulted in empty split after embargo. Reduce embargo_days or provide more data.")

        train_max = self._parse_iso(train[-1].issue_time)
        val_min = self._parse_iso(val[0].issue_time)
        val_max = self._parse_iso(val[-1].issue_time)
        test_min = self._parse_iso(test[0].issue_time)

        if train_max > val_min:
            raise TemporalLeakageError(
                f"Temporal leakage detected: max(train.issue_time) ({train_max}) > min(val.issue_time) ({val_min})"
            )
        if val_max > test_min:
            raise TemporalLeakageError(
                f"Temporal leakage detected: max(val.issue_time) ({val_max}) > min(test.issue_time) ({test_min})"
            )

        return DatasetSplits(
            train_rows=train,
            val_rows=val,
            test_rows=test,
            train_time_range=(train[0].issue_time, train[-1].issue_time),
            val_time_range=(val[0].issue_time, val[-1].issue_time),
            test_time_range=(test[0].issue_time, test[-1].issue_time),
            purged_rows_count=purged_count,
        )


class EventGroupedDataSplitter:
    """Partitions records ensuring no cyclone/monsoon event episode is split across train/test.

    Follows §8.3 & §10.4:
    - Group all leads and related records from a cyclone or monsoon episode so one event cannot appear in both training and test.
    - Preserves chronological order while keeping events intact.
    - Enforces optional temporal embargo between splits to prevent autocorrelation spillover.
    """

    def __init__(
        self,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        event_key: str = "event_id",
        embargo_days: int = 0,
        holdout_event_ids: Optional[List[str]] = None,
    ):
        if not abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5:
            raise ValueError(f"Ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}")
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.event_key = event_key
        self.embargo_days = embargo_days
        self.holdout_event_ids = set(holdout_event_ids or [])

    @staticmethod
    def _parse_iso(iso_str: str) -> datetime:
        return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))

    def _extract_event_id(self, row: HistoricalTrainingRow) -> Optional[str]:
        if hasattr(row, "event_id") and getattr(row, "event_id"):
            return str(getattr(row, "event_id"))
        if hasattr(row, "metadata") and isinstance(row.metadata, dict):
            return row.metadata.get(self.event_key)
        return None

    def split(
        self,
        rows: list[HistoricalTrainingRow],
        event_windows: Optional[List[Dict[str, Any]]] = None,
    ) -> DatasetSplits:
        """Partition rows into Train, Val, and Test ensuring complete event containment.
        
        Args:
            rows: List of historical training rows.
            event_windows: Optional list of explicit event definitions, e.g.:
                [{'event_id': 'amphan_2020', 'start': '2020-05-16T00:00:00Z', 'end': '2020-05-21T00:00:00Z'}]
        """
        if len(rows) < 3:
            raise ValueError(f"Need at least 3 rows for split, got {len(rows)}")

        # 1. Annotate rows with event_id from event_windows if provided
        if event_windows:
            for w in event_windows:
                ev_id = w["event_id"]
                w_start = self._parse_iso(w["start"])
                w_end = self._parse_iso(w["end"])
                for r in rows:
                    r_issue = self._parse_iso(r.issue_time)
                    if w_start <= r_issue <= w_end:
                        if not hasattr(r, "metadata") or r.metadata is None:
                            r.metadata = {}
                        r.metadata[self.event_key] = ev_id

        # 2. Sort rows chronologically
        sorted_rows = sorted(
            rows,
            key=lambda r: (self._parse_iso(r.issue_time), self._parse_iso(r.valid_time)),
        )

        # 3. Group rows into atomic chunks: an event is a chunk; isolated rows are 1-item chunks
        event_to_rows: Dict[str, List[HistoricalTrainingRow]] = {}
        for r in sorted_rows:
            ev_id = self._extract_event_id(r)
            if ev_id:
                event_to_rows.setdefault(ev_id, []).append(r)

        # 4. Partition allocation
        # Separate explicit holdout events if requested (they go straight to test)
        held_out_rows = []
        regular_rows = []
        for r in sorted_rows:
            ev_id = self._extract_event_id(r)
            if ev_id and ev_id in self.holdout_event_ids:
                held_out_rows.append(r)
            else:
                regular_rows.append(r)

        n = len(regular_rows)
        target_train_n = max(1, int(n * self.train_ratio))
        target_val_n = max(1, int(n * self.val_ratio))

        train: List[HistoricalTrainingRow] = []
        val: List[HistoricalTrainingRow] = []
        test: List[HistoricalTrainingRow] = []

        # Greedily assign by chronological order, keeping events intact
        current_split = "train"
        assigned_events: Dict[str, str] = {}  # event_id -> 'train', 'val', or 'test'

        for r in regular_rows:
            ev_id = self._extract_event_id(r)
            if ev_id:
                if ev_id in assigned_events:
                    split_dest = assigned_events[ev_id]
                    if split_dest == "train":
                        train.append(r)
                    elif split_dest == "val":
                        val.append(r)
                    else:
                        test.append(r)
                    continue

                # Decide where to place this new event
                if current_split == "train" and len(train) >= target_train_n:
                    current_split = "val"
                elif current_split == "val" and len(val) >= target_val_n:
                    current_split = "test"

                assigned_events[ev_id] = current_split
                if current_split == "train":
                    train.append(r)
                elif current_split == "val":
                    val.append(r)
                else:
                    test.append(r)
            else:
                # Regular non-event row
                if current_split == "train" and len(train) >= target_train_n:
                    current_split = "val"
                elif current_split == "val" and len(val) >= target_val_n:
                    current_split = "test"

                if current_split == "train":
                    train.append(r)
                elif current_split == "val":
                    val.append(r)
                else:
                    test.append(r)

        # Add explicit holdout events to test
        test.extend(held_out_rows)

        # Ensure all splits have at least one row
        if not test:
            test = [val.pop()] if len(val) > 1 else [train.pop()]
        if not val:
            val = [train.pop()] if len(train) > 1 else [test.pop(0)]

        # 5. Apply temporal embargo if configured
        purged_count = 0
        if self.embargo_days > 0:
            embargo_delta = timedelta(days=self.embargo_days)
            train_max_t = max(self._parse_iso(r.issue_time) for r in train)
            initial_val_len = len(val)
            val = [r for r in val if (self._parse_iso(r.issue_time) - train_max_t) >= embargo_delta]
            purged_count += (initial_val_len - len(val))

            if val:
                val_max_t = max(self._parse_iso(r.issue_time) for r in val)
                initial_test_len = len(test)
                test = [r for r in test if (self._parse_iso(r.issue_time) - val_max_t) >= embargo_delta]
                purged_count += (initial_test_len - len(test))

        # 6. Verify event containment invariant (§8.3)
        train_events = {self._extract_event_id(r) for r in train} - {None}
        val_events = {self._extract_event_id(r) for r in val} - {None}
        test_events = {self._extract_event_id(r) for r in test} - {None}

        train_val_overlap = train_events.intersection(val_events)
        val_test_overlap = val_events.intersection(test_events)
        train_test_overlap = train_events.intersection(test_events)

        if train_val_overlap or val_test_overlap or train_test_overlap:
            raise EventLeakageError(
                f"Event leakage detected! An event was split across partitions: "
                f"train_val={train_val_overlap}, val_test={val_test_overlap}, train_test={train_test_overlap}"
            )

        # Verify temporal monotonicity
        train_max = max(self._parse_iso(r.issue_time) for r in train)
        val_min = min(self._parse_iso(r.issue_time) for r in val)
        val_max = max(self._parse_iso(r.issue_time) for r in val)
        test_min = min(self._parse_iso(r.issue_time) for r in test)

        if train_max > val_min:
            raise TemporalLeakageError(
                f"Temporal leakage detected: max(train.issue_time) ({train_max}) > min(val.issue_time) ({val_min})"
            )
        if val_max > test_min:
            raise TemporalLeakageError(
                f"Temporal leakage detected: max(val.issue_time) ({val_max}) > min(test.issue_time) ({test_min})"
            )

        return DatasetSplits(
            train_rows=train,
            val_rows=val,
            test_rows=test,
            train_time_range=(min(r.issue_time for r in train), max(r.issue_time for r in train)),
            val_time_range=(min(r.issue_time for r in val), max(r.issue_time for r in val)),
            test_time_range=(min(r.issue_time for r in test), max(r.issue_time for r in test)),
            held_out_events=sorted(list(self.holdout_event_ids)),
            purged_rows_count=purged_count,
        )
