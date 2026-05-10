import { useState } from 'react';
import forge from 'node-forge';
import toast, { Toaster } from 'react-hot-toast';
import styles from './TransactionPage.module.css';

const API_URL = import.meta.env.VITE_API_URL;

const TX_TYPES = [
  { id: 'TX', label: 'Transferencia', icon: '⇄', color: '#00d4ff' },
  { id: 'PROPERTY', label: 'Propiedad NFT', icon: '◈', color: '#f0b429' },
  { id: 'TX_NFT', label: 'Transfer NFT', icon: '⟳', color: '#00ff9d' },
];

// --- FUNCIONES DE UTILIDAD (Legacy Logic) ---

const stripPemHeaders = (pemString) => {
  if (!pemString) return "";
  return pemString
    .replace(/-----BEGIN [^-]+-----/, '')
    .replace(/-----END [^-]+-----/, '')
    .replace(/\s+/g, '');
};

const deterministicStringify = (obj) => {
  const sortedKeys = Object.keys(obj).sort();
  const sortedObj = {};
  sortedKeys.forEach(key => { sortedObj[key] = obj[key]; });
  return JSON.stringify(sortedObj);
};

const signDataWithForge = (dataToSign, privateKeyPem) => {
  try {
    const dataString = deterministicStringify(dataToSign);
    let pemToParse = privateKeyPem.trim();
    
    if (!pemToParse.includes('-----BEGIN')) {
      const formatBase64 = (str) => str.match(/.{1,64}/g).join('\n');
      pemToParse = `-----BEGIN RSA PRIVATE KEY-----\n${formatBase64(pemToParse.replace(/\s+/g, ''))}\n-----END RSA PRIVATE KEY-----`;
    }

    const privateKey = forge.pki.privateKeyFromPem(pemToParse);
    const md = forge.md.sha256.create();
    md.update(dataString, 'utf8');
    const signature = privateKey.sign(md);
    
    return forge.util.encode64(signature);
  } catch (error) {
    console.error("Error al procesar la firma:", error);
    throw new Error("Clave privada inválida. Verificá el formato RSA-PEM.");
  }
};

export default function TransactionPage() {
  const [txType, setTxType] = useState('TX');
  const [form, setForm] = useState({ monto: '', origen: '', destino: '', nft: '', owner: '' });
  
  // Estados para nombres de archivos
  const [pubKeyFile, setPubKeyFile] = useState(null);
  const [destPubKeyFile, setDestPubKeyFile] = useState(null);
  const [privKeyFile, setPrivKeyFile] = useState(null);
  
  // Estados para contenidos reales
  const [privKeyContent, setPrivKeyContent] = useState('');
  const [sign, setSign] = useState('');
  const [loading, setLoading] = useState(false);

  const handleField = (k, v) => setForm(f => ({ ...f, [k]: v }));

  // Handlers de archivos
  const handleFileRead = (file, callback) => {
    const reader = new FileReader();
    reader.onload = (e) => callback(e.target.result);
    reader.readAsText(file);
  };

  const handlePubKeyFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPubKeyFile(file.name);
    handleFileRead(file, (content) => {
      const cleaned = stripPemHeaders(content);
      // Dependiendo del tipo, el "origen" puede ser 'origen' o 'owner'
      if (txType === 'PROPERTY') handleField('owner', cleaned);
      else handleField('origen', cleaned);
    });
  };

  const handleDestPubKeyFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setDestPubKeyFile(file.name);
    handleFileRead(file, (content) => {
      handleField('destino', stripPemHeaders(content));
    });
  };

  const handlePrivKeyFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPrivKeyFile(file.name);
    handleFileRead(file, (content) => setPrivKeyContent(content));
  };

  const buildPayloadData = () => {
    // Limpiamos los inputs manuales por si acaso no vinieron de archivo
    const ori = stripPemHeaders(txType === 'PROPERTY' ? form.owner : form.origen);
    const dest = stripPemHeaders(form.destino);

    if (txType === 'TX') {
      return { monto: Number(form.monto), origen: ori, destino: dest };
    }
    if (txType === 'PROPERTY') {
      return { nft: form.nft, owner: ori };
    }
    if (txType === 'TX_NFT') {
      return { nft: form.nft, origen: ori, destino: dest };
    }
  };

  const handleSign = () => {
    if (!privKeyContent) {
      toast.error("Cargá la clave privada para firmar.");
      return;
    }
    try {
      const data = buildPayloadData();
      const signature = signDataWithForge(data, privKeyContent);
      setSign(signature);
      toast.success("Documento firmado correctamente");
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleSubmit = async () => {
    if (!sign) {
      toast.error("Primero debes firmar la transacción.");
      return;
    }

    const data = buildPayloadData();
    const payload = { data, type: txType, sign };

    const loadToast = toast.loading('Enviando a la red UNLUCOIN...');
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/transaccion`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const resultText = await res.text();
      toast.dismiss(loadToast);

      if (!res.ok) {
        try {
          const errorJson = JSON.parse(resultText);
          throw new Error(errorJson.error || `Error ${res.status}`);
        } catch {
          throw new Error(resultText);
        }
      }

      toast.success("¡Transacción enviada con éxito!", { duration: 5000 });
      reset();
    } catch (err) {
      toast.dismiss(loadToast);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setForm({ monto: '', origen: '', destino: '', nft: '', owner: '' });
    setSign('');
    setPubKeyFile(null);
    setDestPubKeyFile(null);
    setPrivKeyFile(null);
    setPrivKeyContent('');
  };

  const selectedType = TX_TYPES.find(t => t.id === txType);

  return (
    <div className={styles.page}>
      {/* Toast Configurado con el estilo de tu página */}
      <Toaster 
        position="top-right"
        toastOptions={{
          style: { 
            background: '#1e293b', 
            color: '#fff', 
            border: '1px solid #334155',
            fontSize: '14px',
            borderRadius: '10px'
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#1e293b' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#1e293b' } },
        }}
      />

      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h1 className={styles.title}>NUEVA TRANSACCIÓN</h1>
          <p className={styles.subtitle}>Firma RSA-4096 local y envío a la red</p>
        </div>
        <div className={styles.headerRight}>
          <div className={styles.blockCount}>
            <span className={styles.blockCountLabel}>NETWORK API</span>
            <span className={styles.blockCountVal}>{API_URL}</span>
          </div>
        </div>
      </div>

      <div className={styles.typeSelector}>
        {TX_TYPES.map(t => (
          <button
            key={t.id}
            className={`${styles.typeBtn} ${txType === t.id ? styles.typeBtnActive : ''}`}
            style={txType === t.id ? { '--type-color': t.color } : {}}
            onClick={() => { setTxType(t.id); reset(); }}
          >
            <span className={styles.typeIcon}>{t.icon}</span>
            <span className={styles.typeId}>{t.id}</span>
            <span className={styles.typeLabel}>{t.label}</span>
          </button>
        ))}
      </div>

      <div className={styles.formCard}>
        <div className={styles.formCardHeader}>
          <span className={styles.formCardIcon} style={{ color: selectedType.color }}>{selectedType.icon}</span>
          <span className={styles.formCardTitle}>Configuración de {txType}</span>
          <div className={styles.formCardLine} style={{ background: selectedType.color }} />
        </div>

        <div className={styles.fields}>
          {/* Campos dinámicos según el tipo */}
          {txType === 'TX' && (
            <Field label="MONTO" hint="Cantidad a transferir">
              <input
                className={styles.input}
                type="number"
                placeholder="0.00"
                value={form.monto}
                onChange={e => handleField('monto', e.target.value)}
              />
            </Field>
          )}

          {(txType === 'PROPERTY' || txType === 'TX_NFT') && (
            <Field label="NFT ID" hint="Hash único del activo">
              <input
                className={styles.input}
                placeholder="ID del NFT"
                value={form.nft}
                onChange={e => handleField('nft', e.target.value)}
              />
            </Field>
          )}

          {/* ORIGEN / OWNER */}
          <Field label={txType === 'PROPERTY' ? "DUEÑO (OWNER)" : "ORIGEN"} hint="Clave pública del emisor">
            <div className={styles.inputWithFile}>
              <input
                className={styles.input}
                placeholder="Pegar clave o subir archivo..."
                value={pubKeyFile ? `Archivo: ${pubKeyFile}` : (txType === 'PROPERTY' ? form.owner : form.origen)}
                onChange={e => handleField(txType === 'PROPERTY' ? 'owner' : 'origen', e.target.value)}
                readOnly={!!pubKeyFile}
              />
              <label className={styles.fileBtn}>
                📂 {pubKeyFile ? 'Cambiar' : 'Archivo'}
                <input type="file" accept=".pem,.pub,.key,.txt" onChange={handlePubKeyFile} hidden />
              </label>
            </div>
          </Field>

          {/* DESTINO */}
          {(txType === 'TX' || txType === 'TX_NFT') && (
            <Field label="DESTINO" hint="Clave pública del receptor">
              <div className={styles.inputWithFile}>
                <input
                  className={styles.input}
                  placeholder="Pegar clave o subir archivo..."
                  value={destPubKeyFile ? `Archivo: ${destPubKeyFile}` : form.destino}
                  onChange={e => handleField('destino', e.target.value)}
                  readOnly={!!destPubKeyFile}
                />
                <label className={styles.fileBtn}>
                  📂 {destPubKeyFile ? 'Cambiar' : 'Archivo'}
                  <input type="file" accept=".pem,.pub,.key,.txt" onChange={handleDestPubKeyFile} hidden />
                </label>
              </div>
            </Field>
          )}

          <div className={styles.divider}>
            <span>SEGURIDAD</span>
          </div>

          <Field label="CLAVE PRIVADA (RSA)" hint="Se usa solo para firmar localmente">
            <div className={styles.inputWithFile}>
              <input
                className={styles.input}
                placeholder="Seleccioná tu archivo .pem..."
                value={privKeyFile || ''}
                readOnly
              />
              <label className={styles.fileBtn} style={{ background: '#10b981', color: '#000' }}>
                🔑 {privKeyFile ? 'Cargada' : 'Cargar'}
                <input type="file" accept=".pem,.key,.txt" onChange={handlePrivKeyFile} hidden />
              </label>
            </div>
          </Field>

          <Field label="FIRMA DIGITAL" hint="Resultado de la firma SHA256withRSA">
            <div className={styles.signRow}>
              <input
                className={styles.input}
                placeholder="Haz clic en FIRMAR para generar"
                value={sign}
                readOnly
              />
              <button className={styles.signBtn} onClick={handleSign}>
                ✎ FIRMAR
              </button>
            </div>
          </Field>
        </div>

        <div className={styles.actions}>
          <button className={styles.resetBtn} onClick={reset}>↺ LIMPIAR</button>
          <button
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={loading || !sign}
          >
            {loading ? <span className={styles.spinner} /> : <>⟶ ENVIAR TRANSACCIÓN</>}
          </button>
        </div>

        <details className={styles.preview}>
          <summary className={styles.previewSummary}>Ver Payload Final (JSON)</summary>
          <pre className={styles.previewCode}>
            {JSON.stringify({
                data: buildPayloadData(),
                type: txType,
                sign: sign
              }, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}

function Field({ label, hint, children }) {
  return (
    <div className={styles.field}>
      <label className={styles.label}>
        {label}
        {hint && <span className={styles.hint}>{hint}</span>}
      </label>
      {children}
    </div>
  );
}