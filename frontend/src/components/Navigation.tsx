import React, { useState, useEffect, useRef } from 'react';
import { Crosshair, Layers, Cpu, FileCode, ExternalLink, Menu, X, History, Compass, BarChart3 } from 'lucide-react';

export type ActiveView = 'sentinel' | 'replay' | 'analogs' | 'metrics' | 'batch' | 'models' | 'docs';

const DOCS_EXTERNAL_URL = 'https://veyra-know-when-forecasts-may-fail.onrender.com/docs';

interface NavigationProps {
  view: ActiveView;
  setView: (view: ActiveView) => void;
  onOpenProvenance?: () => void;
}

export const Navigation: React.FC<NavigationProps> = ({ view, setView, onOpenProvenance }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent | TouchEvent) {
      if (navRef.current && !navRef.current.contains(event.target as Node)) {
        setMobileMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, []);

  const handleSelectView = (newView: ActiveView) => {
    setView(newView);
    setMobileMenuOpen(false);
  };

  return (
    <nav className="dropdown-nav" ref={navRef} aria-label="Main Navigation">
      {/* Mobile Menu Toggle Button */}
      <div className="mobile-nav-header">
        <button
          className="mobile-menu-btn"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle Navigation Menu"
          aria-expanded={mobileMenuOpen}
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          <span>Menu</span>
        </button>
        <span className="mobile-current-view">
          {view === 'sentinel'
            ? 'Reliability Sentinel'
            : view === 'replay'
            ? 'Historical Replay'
            : view === 'analogs'
            ? 'Analog Explorer'
            : view === 'metrics'
            ? 'Research Metrics'
            : view === 'batch'
            ? 'Batch Evaluation'
            : view === 'models'
            ? 'Model Registry'
            : 'API Documentation'}
        </span>
      </div>

      {/* Nav Items Container */}
      <div className={`nav-items-container ${mobileMenuOpen ? 'mobile-open' : ''}`}>
        {/* Reliability Sentinel Direct Button */}
        <div className="dropdown">
          <button
            type="button"
            className={view === 'sentinel' ? 'active' : ''}
            onClick={() => handleSelectView('sentinel')}
          >
            <Crosshair size={16} /> Reliability Sentinel
          </button>
        </div>

        {/* Replay View (SIH §20 Demo Mode) */}
        <div className="dropdown">
          <button
            type="button"
            className={view === 'replay' ? 'active' : ''}
            onClick={() => handleSelectView('replay')}
          >
            <History size={16} /> Historical Replay
            <span
              style={{
                marginLeft: '6px',
                background: '#ffd200',
                color: '#002b49',
                padding: '2px 6px',
                borderRadius: '8px',
                fontSize: '0.68rem',
                fontWeight: 800,
              }}
            >
              §20 Demo
            </span>
          </button>
        </div>

        {/* Analog Explorer */}
        <div className="dropdown">
          <button
            type="button"
            className={view === 'analogs' ? 'active' : ''}
            onClick={() => handleSelectView('analogs')}
          >
            <Compass size={16} /> Analog Explorer
          </button>
        </div>

        {/* Research Metrics (§18.1) */}
        <div className="dropdown">
          <button
            type="button"
            className={view === 'metrics' ? 'active' : ''}
            onClick={() => handleSelectView('metrics')}
          >
            <BarChart3 size={16} /> Research Metrics
          </button>
        </div>

        {/* Batch Evaluation (25 Stations) Direct Button */}
        <div className="dropdown">
          <button
            type="button"
            className={view === 'batch' ? 'active' : ''}
            onClick={() => handleSelectView('batch')}
          >
            <Layers size={16} /> Batch Evaluation
          </button>
        </div>

        {/* Model Registry Button */}
        <div className="dropdown">
          <button
            type="button"
            className={view === 'models' ? 'active' : ''}
            onClick={() => handleSelectView('models')}
          >
            <Cpu size={16} /> Model Registry
          </button>
        </div>

        {/* Embedded API Docs Button */}
        <div className="dropdown">
          <button
            type="button"
            className={view === 'docs' ? 'active' : ''}
            onClick={() => handleSelectView('docs')}
          >
            <FileCode size={16} /> API Docs
          </button>
        </div>

        {/* Provenance Drawer Button */}
        {onOpenProvenance && (
          <div className="dropdown">
            <button
              type="button"
              onClick={onOpenProvenance}
              style={{
                background: 'rgba(255, 255, 255, 0.1)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: 'var(--noaa-white)',
              }}
            >
              Lineage &amp; Provenance
            </button>
          </div>
        )}

        {/* External API Docs Link */}
        <div className="nav-external-link">
          <a
            href={DOCS_EXTERNAL_URL}
            target="_blank"
            rel="noreferrer"
            title="Open Swagger in new tab"
          >
            Open Swagger <ExternalLink size={13} />
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;

