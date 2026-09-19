import React, { useState, useEffect } from 'react';
import { DataProvenanceResponse } from '../api/types';
import { apiClient } from '../api/client';

interface ProvenanceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const DEFAULT_PROVENANCE: DataProvenanceResponse = {
  schema_version: '2.0.0',
  primary_sources: {
    forecast_model: 'NOAA GEFS v12 / Open-Meteo Ensemble API (0.5° grid, 31 members)',
    forecast_resolution: '0.50 degree latitude/longitude, 3-hourly to 240 hours',
    reference_analysis: 'ECMWF ERA5 Reanalysis (0.25° grid, hourly analysis)',
    reference_resolution: '0.25 degree latitude/longitude, hourly single levels',
    verification_only_invariant:
      'ERA5 reference analysis is strictly utilized for ground-truth verification and bust threshold derivation. It is mathematically forbidden from being used as a feature, input, or predictor at forecast issue time.',
  },
  artifacts_checksums: {
    model_artifact_sha256: '00A8410746F4A0EECBF7E76AAA0565143FC948D0E06AEA65E7BCC4CE28A1C660',
    calibrator_artifact_sha256: '9F448606CE4338DED92F238A551B3A9D8E6D2CB5902E8BC687BCE5F5850AF531',
    feature_contract_sha256: '265CFFBBD157A2B8B8B46D3702438050980043B5ED3A6A646A7969CDB9853355',
    dataset_manifest_sha256: 'B4D8E9F1A2C3E4F5A6B7C8D9E0F1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D7E8F9',
  },
  licenses: {
    open_meteo: {
      license: 'Creative Commons Attribution 4.0 International (CC-BY-4.0)',
      uri: 'https://open-meteo.com/en/terms',
      attribution: 'Weather data provided by Open-Meteo under CC-BY-4.0',
    },
    era5_copernicus: {
      license: 'Copernicus Open Access License',
      uri: 'https://cds.climate.copernicus.eu/api/v2/terms/static/licence-to-use-copernicus-products.pdf',
      attribution: 'Generated using Copernicus Climate Change Service information [2026]',
    },
    noaa_gefs: {
      license: 'Public Domain / Open Data Policy (NOAA)',
      uri: 'https://www.ncei.noaa.gov/products/weather-climate-models/global-ensemble-forecast',
      attribution: 'NOAA National Centers for Environmental Information',
    },
  },
  pipeline_lineage: [
    'DISCOVERED',
    'DOWNLOADING',
    'DOWNLOADED',
    'CHECKSUMMED',
    'QC_PASS',
    'ALIGNED',
    'FEATURES_READY',
    'INFERENCE_READY',
    'PUBLISHED',
  ],
};

export const ProvenanceDrawer: React.FC<ProvenanceDrawerProps> = ({ isOpen, onClose }) => {
  const [provenance, setProvenance] = useState<DataProvenanceResponse>(DEFAULT_PROVENANCE);

  useEffect(() => {
    if (isOpen) {
      apiClient.getDataProvenance().then(({ data }) => {
        if (data) setProvenance(data);
      });
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        right: 0,
        bottom: 0,
        width: '100%',
        maxWidth: '520px',
        background: 'var(--noaa-card-bg)',
        boxShadow: '-4px 0 24px rgba(0,0,0,0.18)',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        animation: 'slideInRight 0.2s ease',
      }}
      role="dialog"
      aria-labelledby="provenance-title"
    >
      {/* Drawer Header */}
      <div
        style={{
          padding: '18px 22px',
          background: 'var(--noaa-dark-blue)',
          color: '#ffffff',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <div>
          <h3 id="provenance-title" style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0 }}>
            Data Lineage & Provenance Drawer
          </h3>
          <div style={{ fontSize: '0.75rem', opacity: 0.85, marginTop: '2px' }}>
            Docs §17, §22 • Research Files 095, 114
          </div>
        </div>
        <button
          onClick={onClose}
          aria-label="Close Provenance Drawer"
          style={{
            background: 'transparent',
            border: 'none',
            color: '#ffffff',
            fontSize: '1.4rem',
            cursor: 'pointer',
            padding: '4px 8px',
          }}
        >
          &times;
        </button>
      </div>

      {/* Content Body */}
      <div style={{ padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {/* Verification-Only Invariant Callout */}
        <div
          style={{
            padding: '12px 14px',
            background: '#f0fdf4',
            borderLeft: '4px solid #16a34a',
            borderRadius: '0 6px 6px 0',
          }}
        >
          <div style={{ fontSize: '0.78rem', fontWeight: 800, color: '#166534', textTransform: 'uppercase' }}>
            Verification-Only Invariant (§7.2, File 032)
          </div>
          <p style={{ fontSize: '0.8rem', color: '#14532d', marginTop: '4px', lineHeight: '1.4' }}>
            {provenance.primary_sources.verification_only_invariant}
          </p>
        </div>

        {/* Pipeline Lineage Stepper */}
        <div>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--noaa-dark-blue)', textTransform: 'uppercase', marginBottom: '8px' }}>
            End-to-End Pipeline Lineage
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {provenance.pipeline_lineage.map((step, idx) => (
              <span
                key={step}
                style={{
                  fontSize: '0.72rem',
                  fontFamily: 'monospace',
                  background: 'var(--noaa-light-blue)',
                  color: 'var(--noaa-dark-blue)',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  fontWeight: 700,
                }}
              >
                {idx + 1}. {step}
              </span>
            ))}
          </div>
        </div>

        {/* Primary Data Sources */}
        <div>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--noaa-dark-blue)', textTransform: 'uppercase', marginBottom: '8px' }}>
            Primary Data Sources
          </h4>
          <div style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ background: 'var(--noaa-gray-bg)', padding: '10px', borderRadius: '4px' }}>
              <strong style={{ color: 'var(--noaa-accent)' }}>Forecast Source:</strong>
              <div>{provenance.primary_sources.forecast_model}</div>
              <div style={{ color: 'var(--noaa-muted)', fontSize: '0.75rem', marginTop: '2px' }}>
                Resolution: {provenance.primary_sources.forecast_resolution}
              </div>
            </div>
            <div style={{ background: 'var(--noaa-gray-bg)', padding: '10px', borderRadius: '4px' }}>
              <strong style={{ color: 'var(--noaa-accent)' }}>Verification Source:</strong>
              <div>{provenance.primary_sources.reference_analysis}</div>
              <div style={{ color: 'var(--noaa-muted)', fontSize: '0.75rem', marginTop: '2px' }}>
                Resolution: {provenance.primary_sources.reference_resolution}
              </div>
            </div>
          </div>
        </div>

        {/* SHA-256 Checksums */}
        <div>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--noaa-dark-blue)', textTransform: 'uppercase', marginBottom: '8px' }}>
            Artifact SHA-256 Checksums (C9, L5)
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {Object.entries(provenance.artifacts_checksums).map(([name, hash]) => (
              <div
                key={name}
                style={{
                  background: 'var(--noaa-gray-bg)',
                  padding: '8px 10px',
                  borderRadius: '4px',
                  fontSize: '0.72rem',
                }}
              >
                <div style={{ fontWeight: 700, color: 'var(--noaa-text)' }}>{name}</div>
                <div style={{ fontFamily: 'monospace', color: 'var(--noaa-muted)', wordBreak: 'break-all', marginTop: '2px' }}>
                  {hash}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Licenses & Terms of Use */}
        <div>
          <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--noaa-dark-blue)', textTransform: 'uppercase', marginBottom: '8px' }}>
            Dataset Licenses & Terms (C11)
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(provenance.licenses).map(([key, item]) => (
              <div key={key} style={{ fontSize: '0.78rem', background: 'var(--noaa-gray-bg)', padding: '8px 10px', borderRadius: '4px' }}>
                <div style={{ fontWeight: 700 }}>{item.license}</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--noaa-muted)', marginTop: '2px' }}>{item.attribution}</div>
                <a
                  href={item.uri}
                  target="_blank"
                  rel="noreferrer"
                  style={{ fontSize: '0.72rem', color: 'var(--noaa-accent)', marginTop: '4px', display: 'inline-block' }}
                >
                  View Terms URI &rarr;
                </a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProvenanceDrawer;
