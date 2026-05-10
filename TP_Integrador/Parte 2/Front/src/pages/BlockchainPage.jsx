import { useState, useEffect, useCallback } from 'react';
import styles from './BlockchainPage.module.css';

const API_URL = import.meta.env.VITE_API_URL;

function truncate(str, n = 14) {
  if (!str || str === 'None') return '—';
  const s = String(str);
  if (s.length <= n + 6) return s;
  return s.slice(0, n) + '…' + s.slice(-6);
}

function formatTime(ts) {
  if (!ts) return '—';
  return new Date(Number(ts) * 1000).toLocaleString('es-AR', {
    day: '2-digit', month: '2-digit', year: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  });
}

const TX_COLORS = { TX: '#00d4ff', PROPERTY: '#f0b429', TX_NFT: '#00ff9d' };
const TX_ICONS  = { TX: '⇄', PROPERTY: '◈', TX_NFT: '⟳' };

function TxBadge({ type }) {
  const color = TX_COLORS[type] || '#aaa';
  return (
    <span className={styles.txBadge} style={{ color, borderColor: color }}>
      {TX_ICONS[type] || '?'} {type || '?'}
    </span>
  );
}

function CopyBtn({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(String(text));
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <button className={styles.copyBtn} onClick={copy} title="Copiar">
      {copied ? '✓' : '⎘'}
    </button>
  );
}

function HashField({ label, value }) {
  return (
    <div className={styles.hashField}>
      <span className={styles.hashLabel}>{label}</span>
      <div className={styles.hashValRow}>
        <span className={styles.hashVal} title={value}>{value && value !== 'None' ? value : '—'}</span>
        {value && value !== 'None' && <CopyBtn text={value} />}
      </div>
    </div>
  );
}

function DataRow({ label, val, accent }) {
  return (
    <div className={styles.dataRow}>
      <span className={styles.dataLabel}>{label}</span>
      <span className={styles.dataVal} style={accent ? { color: accent } : {}}>{val ?? '—'}</span>
    </div>
  );
}

function TransactionCard({ tx, idx }) {
  const [open, setOpen] = useState(false);
  const { data, type, sign } = tx;
  const color = TX_COLORS[type] || '#aaa';

  return (
    <div className={styles.txCard} style={{ '--tx-color': color }}>
      <div className={styles.txCardHeader} onClick={() => setOpen(o => !o)}>
        <TxBadge type={type} />
        <span className={styles.txCardIdx}>TX #{idx + 1}</span>

        {type === 'TX' && (
          <span className={styles.txSummary}>
            <span style={{ color: '#ff7b7b' }}>{truncate(data.origen, 8)}</span>
            <span style={{ color: '#aaa' }}> → </span>
            <span style={{ color: '#7bffbe' }}>{truncate(data.destino, 8)}</span>
            <span className={styles.txMonto}>{data.monto} ULC</span>
          </span>
        )}
        {type === 'TX_NFT' && (
          <span className={styles.txSummary}>
            <span style={{ color: '#f0b429' }}>NFT</span>
            <span style={{ color: '#aaa' }}> {truncate(data.nft, 10)} </span>
            <span style={{ color: '#aaa' }}>→ {truncate(data.destino, 8)}</span>
          </span>
        )}
        {type === 'PROPERTY' && (
          <span className={styles.txSummary}>
            <span style={{ color: '#f0b429' }}>NFT</span>
            <span style={{ color: '#aaa' }}> {truncate(data.nft, 10)} </span>
            <span style={{ color: '#7bffbe' }}>owner: {truncate(data.owner, 8)}</span>
          </span>
        )}

        <span className={`${styles.txChevron} ${open ? styles.txChevronOpen : ''}`}>▾</span>
      </div>

      {open && (
        <div className={styles.txCardBody}>
          <div className={styles.txFields}>
            {type === 'TX' && <>
              <TxField label="MONTO" val={`${data.monto} ULC`} accent="var(--accent-gold)" />
              <TxField label="ORIGEN" val={data.origen} mono full />
              <TxField label="DESTINO" val={data.destino} mono full />
            </>}
            {type === 'PROPERTY' && <>
              <TxField label="NFT HASH" val={data.nft} mono full />
              <TxField label="OWNER" val={data.owner} mono full />
            </>}
            {type === 'TX_NFT' && <>
              <TxField label="NFT HASH" val={data.nft} mono full />
              <TxField label="ORIGEN" val={data.origen} mono full />
              <TxField label="DESTINO" val={data.destino} mono full />
            </>}
          </div>
          {sign && (
            <div className={styles.signSection}>
              <span className={styles.signLabel}>FIRMA (sign)</span>
              <div className={styles.signValRow}>
                <span className={styles.signVal}>{sign}</span>
                <CopyBtn text={sign} />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function TxField({ label, val, mono, accent, full }) {
  return (
    <div className={`${styles.txField} ${full ? styles.txFieldFull : ''}`}>
      <span className={styles.txFieldLabel}>{label}</span>
      <div className={styles.txFieldValRow}>
        <span
          className={`${styles.txFieldVal} ${mono ? styles.txFieldValMono : ''}`}
          style={accent ? { color: accent } : {}}
          title={val}
        >
          {val ?? '—'}
        </span>
        {val && <CopyBtn text={val} />}
      </div>
    </div>
  );
}

function BlockCard({ block, index, total }) {
  const [expanded, setExpanded] = useState(false);
  const txList = Array.isArray(block.transaccion) ? block.transaccion : [];
  const blockNum = block.numero ?? index;
  const isGenesis = !block.previous_block || block.previous_block === 'None';

  return (
    <div className={styles.blockWrap}>
      {/* Chain link between blocks */}
      {index < total  && (
        <div className={styles.chainLink}>
          <div className={styles.chainLinkLine} />
          <span className={styles.chainLinkArrow}>▼</span>
          <div className={styles.chainLinkLine} />
        </div>
      )}

      <div className={`${styles.blockCard} ${expanded ? styles.blockCardOpen : ''} ${isGenesis ? styles.blockCardGenesis : ''}`}>
        {/* Glow bar */}
        <div className={styles.blockGlowBar} />

        {/* Header row */}
        <div className={styles.blockHeader} onClick={() => setExpanded(e => !e)}>
          <div className={styles.blockNumBadge}>
            {isGenesis && <span className={styles.genesisBadge}>GÉNESIS</span>}
            <span className={styles.blockNumLabel}>BLOQUE</span>
            <span className={styles.blockNumVal}>#{String(blockNum).padStart(4, '0')}</span>
          </div>

          {/* Hash chips */}
          <div className={styles.hashChips}>
            <div className={styles.hashChip}>
              <span className={styles.hashChipLabel}>HASH</span>
              <span className={styles.hashChipVal}>{truncate(block.hash, 8)}</span>
            </div>
            <div className={styles.hashChipArrow}>←</div>
            <div className={styles.hashChip}>
              <span className={styles.hashChipLabel}>PREV</span>
              <span className={styles.hashChipVal} style={{ color: isGenesis ? 'var(--text-dim)' : undefined }}>
                {isGenesis ? 'GENESIS' : truncate(block.previous_block, 8)}
              </span>
            </div>
          </div>

          <div className={styles.blockMeta}>
            <MetaPill label="TXs" val={txList.length} color="var(--accent-gold)" />
            <MetaPill label="PREFIX" val={block.prefix} color="var(--accent-green)" />
            <MetaPill label="TIMESTAMP" val={formatTime(block.timestamp)} />
          </div>

          <button className={`${styles.expandBtn} ${expanded ? styles.expandBtnOpen : ''}`}>▾</button>
        </div>

        {/* Chips row */}
        <div className={styles.chipsRow}>
          {[
            ['ID', block.id ? truncate(block.id, 8) : '—'],
            ['HASH', block.hash ? truncate(block.hash, 8) : '—'],
            ['TX[]', txList.length],
            ['PREFIX', block.prefix ?? '—'],
            ['STR', block.base_string_chain ?? '—'],
            ['BC_CONT', block.blockchain_content ? truncate(block.blockchain_content, 6) : '—'],
            ['P_TIME', block.tiempo_proceso != null ? `${block.tiempo_proceso.toFixed(4)}s` : '—'],
            ['NUMB', blockNum],
            ['PREV_BLOCK', block.previous_block && block.previous_block !== 'None' ? truncate(block.previous_block, 6) : 'NONE'],
          ].map(([k, v]) => (
            <div key={k} className={styles.chipItem}>
              <span className={styles.chipKey}>{k}</span>
              <span className={styles.chipVal}>{v}</span>
            </div>
          ))}
        </div>

        {/* Expanded body */}
        {expanded && (
          <div className={styles.blockBody}>
            {/* Full hash fields */}
            <div className={styles.hashFields}>
              <HashField label="HASH DEL BLOQUE" value={block.hash} />
              <HashField label="BLOQUE ANTERIOR" value={block.previous_block} />
              <HashField label="BLOCKCHAIN CONTENT" value={block.blockchain_content} />
            </div>

            {/* Metadata grid */}
            <div className={styles.metaGrid}>
              <DataRow label="ID" val={block.id} />
              <DataRow label="NÚMERO" val={blockNum} accent="var(--accent-cyan)" />
              <DataRow label="PREFIX" val={block.prefix} accent="var(--accent-green)" />
              <DataRow label="BASE STRING" val={block.base_string_chain} />
              <DataRow label="TIEMPO DE PROCESO" val={block.tiempo_proceso != null ? `${block.tiempo_proceso.toFixed(6)}s` : '—'} />
              <DataRow label="TIMESTAMP" val={formatTime(block.timestamp)} />
            </div>

            {/* Transactions */}
            <div className={styles.txSection}>
              <div className={styles.txSectionTitle}>
                <span>TRANSACCIONES</span>
                <span className={styles.txCount}>{txList.length}</span>
              </div>
              {txList.length === 0
                ? <div className={styles.noTxs}>Sin transacciones</div>
                : txList.map((tx, i) => <TransactionCard key={i} tx={tx} idx={i} />)
              }
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MetaPill({ label, val, color }) {
  return (
    <div className={styles.metaPill}>
      <span className={styles.metaPillLabel}>{label}</span>
      <span className={styles.metaPillVal} style={color ? { color } : {}}>{val ?? '—'}</span>
    </div>
  );
}

function Stat({ label, val, color }) {
  return (
    <div className={styles.stat}>
      <span className={styles.statLabel}>{label}</span>
      <span className={styles.statVal} style={{ color }}>{val}</span>
    </div>
  );
}

export default function BlockchainPage() {
  const [blocks, setBlocks] = useState([]);
  const [prefijo, setPrefijo] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lastFetch, setLastFetch] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const fetchBlocks = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/blockchain`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const list = Array.isArray(data) ? data : (data.blocks || data.chain || []);
      // Sort by numero desc (newest first)
      list.sort((a, b) => (b.id ?? 0) - (a.id ?? 0));
      setBlocks(list);
      setLastFetch(new Date());
    } catch (err) {
      setError(`No se pudo conectar a ${API_URL}/blockchain — ${err.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

const fetchPrefijo = useCallback(async () => {
  try {
    const res = await fetch(`${API_URL}/prefijo`);
    
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    
    // IMPORTANTE: Usamos .text() en lugar de .json() 
    // porque el backend devuelve un texto/string directamente.
    const data = await res.text(); 
    
    setPrefijo(data); // Guardamos el valor en el estado
  } catch (err) {
    console.error(`Error obteniendo el prefijo: ${err.message}`);
    // Opcional: manejar el error visualmente con un toast o estado de error
    // setError(`No se pudo obtener el prefijo — ${err.message}`);
  }
}, []);


  useEffect(() => { fetchBlocks(); fetchPrefijo();}, [fetchBlocks,fetchPrefijo]);

  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(fetchBlocks, 5000);
    return () => clearInterval(id);
  }, [autoRefresh, fetchBlocks]);

  const totalTxs = blocks.reduce((acc, b) => acc + (Array.isArray(b.transaccion) ? b.transaccion.length : 0), 0);

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>BLOCKCHAIN</h1>
          <p className={styles.subtitle}>Estado en tiempo real de la cadena de bloques · Redis DB</p>
        </div>
        <div className={styles.headerRight}>
          <div className={styles.statsRow}>
            <Stat label="BLOQUES" val={blocks.length} color="var(--accent-cyan)" />
            <Stat label="TXs TOTALES" val={totalTxs} color="var(--accent-gold)" />
            <Stat label="PREFIJO ACTUAL" val={prefijo} color="var(--accent-green)" />
          </div>
          <div className={styles.controls}>
            <button className={`${styles.refreshBtn} ${loading ? styles.refreshLoading : ''}`} onClick={fetchBlocks} disabled={loading}>
              {loading ? <span className={styles.spinner} /> : '↻'} ACTUALIZAR
            </button>
            <button className={`${styles.autoBtn} ${autoRefresh ? styles.autoBtnOn : ''}`} onClick={() => setAutoRefresh(a => !a)}>
              {autoRefresh ? '■ LIVE ON' : '▶ LIVE'}
            </button>
          </div>
          {lastFetch && <span className={styles.lastFetch}>Actualizado: {lastFetch.toLocaleTimeString('es-AR')}</span>}
        </div>
      </div>

      {error && <div className={styles.errorMsg}><span>⚠</span>{error}</div>}

      {loading && blocks.length === 0 && (
        <div className={styles.loadingWrap}>
          <div className={styles.loadingSpinner} />
          <span>Conectando con la blockchain...</span>
        </div>
      )}

      {!loading && !error && blocks.length === 0 && (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>⛓</div>
          <div className={styles.emptyText}>BLOCKCHAIN VACÍA</div>
          <div className={styles.emptyHint}>Enviá una transacción para crear el primer bloque</div>
        </div>
      )}

      <div className={styles.chain}>
        {blocks.map((block, i) => (
          <BlockCard key={block.id || i} block={block} index={i} total={blocks.length} />
        ))}
      </div>
    </div>
  );
}
