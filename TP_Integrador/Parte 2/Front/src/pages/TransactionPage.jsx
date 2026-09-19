import { useState, useRef, useEffect } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import styles from './TransactionPage.module.css';
import WalletModal from '../components/WalletModal';
import {
  stripPemHeaders,
  signDataWithForge,
  generateRSAKeyPair,
  getStoredWallets,
  saveStoredWallet,
} from '../utils/crypto';

const API_URL = import.meta.env.VITE_API_URL;

const TX_TYPES = [
  { id: 'TX', label: 'Transferencia', icon: '⇄', color: '#00d4ff' },
  { id: 'PROPERTY', label: 'Propiedad NFT', icon: '◈', color: '#f0b429' },
  { id: 'TX_NFT', label: 'Transfer NFT', icon: '⟳', color: '#00ff9d' },
];

export default function TransactionPage() {
  const [txType, setTxType] = useState('TX');
  const [form, setForm] = useState({
    monto: '',
    origen: '',
    destino: '',
    nft: '',
    owner: '',
  });

  // Nombres de archivos o cuentas activas
  const [pubKeyFile, setPubKeyFile] = useState(null);
  const [destPubKeyFile, setDestPubKeyFile] = useState(null);
  const [privKeyFile, setPrivKeyFile] = useState(null);

  // Metadata de cuentas seleccionadas
  const [originWalletName, setOriginWalletName] = useState('');
  const [destWalletName, setDestWalletName] = useState('');

  // Contenido de clave privada y firma
  const [privKeyContent, setPrivKeyContent] = useState('');
  const [sign, setSign] = useState('');
  const [loading, setLoading] = useState(false);

  // Modal de Billeteras
  const [isWalletModalOpen, setIsWalletModalOpen] = useState(false);
  const [generatingOrigin, setGeneratingOrigin] = useState(false);
  const [generatingDest, setGeneratingDest] = useState(false);
  const [walletCount, setWalletCount] = useState(0);

  // Refs para resetear inputs file
  const pubKeyInputRef = useRef(null);
  const destPubKeyInputRef = useRef(null);
  const privKeyInputRef = useRef(null);

  useEffect(() => {
    updateWalletCount();
  }, []);

  const updateWalletCount = () => {
    const list = getStoredWallets();
    setWalletCount(list.length);
  };

  const handleField = (k, v) => {
    setForm((f) => ({ ...f, [k]: v }));
    // Si editan a mano, limpiar nombre de archivo / badge si corresponde
    if (k === 'origen' || k === 'owner') {
      setPubKeyFile(null);
    }
    if (k === 'destino') {
      setDestPubKeyFile(null);
    }
  };

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
    setOriginWalletName('');
    handleFileRead(file, (content) => {
      const cleaned = stripPemHeaders(content);
      if (txType === 'PROPERTY') handleField('owner', cleaned);
      else handleField('origen', cleaned);
    });
  };

  const handleDestPubKeyFile = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setDestPubKeyFile(file.name);
    setDestWalletName('');
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

  // Selección de Billeteras desde el Modal o Gestor
  const handleSelectOriginWallet = (wallet) => {
    const cleaned = wallet.publicKeyClean || stripPemHeaders(wallet.publicKeyPem);
    if (txType === 'PROPERTY') {
      handleField('owner', cleaned);
    } else {
      handleField('origen', cleaned);
    }
    setOriginWalletName(wallet.name || 'Billetera Local');
    setPubKeyFile(null);

    if (wallet.privateKeyPem) {
      setPrivKeyContent(wallet.privateKeyPem);
      setPrivKeyFile(`⚡ En memoria (${wallet.name || 'Generada'})`);
    }
    setSign('');
  };

  const handleSelectDestWallet = (wallet) => {
    const cleaned = wallet.publicKeyClean || stripPemHeaders(wallet.publicKeyPem);
    handleField('destino', cleaned);
    setDestWalletName(wallet.name || 'Billetera Local');
    setDestPubKeyFile(null);
  };

  // Generación rápida al vuelo para ORIGEN
  const handleQuickGenerateOrigin = async () => {
    setGeneratingOrigin(true);
    const toastId = toast.loading('Generando par de claves RSA (2048 bits)...');
    try {
      await new Promise((r) => setTimeout(r, 50));
      const keypair = await generateRSAKeyPair(2048);
      const name = `Billetera #${getStoredWallets().length + 1}`;
      
      // Auto-guardar en local storage
      saveStoredWallet({
        name,
        privateKeyPem: keypair.privateKeyPem,
        publicKeyPem: keypair.publicKeyPem,
        publicKeyClean: keypair.publicKeyClean,
      });
      updateWalletCount();

      // Aplicar al formulario
      handleSelectOriginWallet({
        name,
        publicKeyClean: keypair.publicKeyClean,
        privateKeyPem: keypair.privateKeyPem,
      });

      toast.success(`¡Claves generadas y guardadas como "${name}"!`, { id: toastId });
    } catch (err) {
      console.error(err);
      toast.error('Error al generar claves: ' + err.message, { id: toastId });
    } finally {
      setGeneratingOrigin(false);
    }
  };

  // Generación rápida al vuelo para DESTINO
  const handleQuickGenerateDest = async () => {
    setGeneratingDest(true);
    const toastId = toast.loading('Generando clave de destino RSA...');
    try {
      await new Promise((r) => setTimeout(r, 50));
      const keypair = await generateRSAKeyPair(2048);
      const name = `Destinatario #${getStoredWallets().length + 1}`;

      saveStoredWallet({
        name,
        privateKeyPem: keypair.privateKeyPem,
        publicKeyPem: keypair.publicKeyPem,
        publicKeyClean: keypair.publicKeyClean,
      });
      updateWalletCount();

      handleSelectDestWallet({
        name,
        publicKeyClean: keypair.publicKeyClean,
      });

      toast.success(`Destino configurado como "${name}"`, { id: toastId });
    } catch (err) {
      console.error(err);
      toast.error('Error: ' + err.message, { id: toastId });
    } finally {
      setGeneratingDest(false);
    }
  };

  // Test Rápido / Demo Autofill
  const handleQuickDemo = async () => {
    const toastId = toast.loading('Preparando transacción de prueba...');
    try {
      const wallets = getStoredWallets();
      let sender, receiver;

      if (wallets.length >= 2) {
        sender = wallets[0];
        receiver = wallets[1];
      } else {
        // Generar 2 cuentas si no existen
        const k1 = await generateRSAKeyPair(2048);
        sender = saveStoredWallet({
          name: 'Alicia (Demo)',
          privateKeyPem: k1.privateKeyPem,
          publicKeyPem: k1.publicKeyPem,
          publicKeyClean: k1.publicKeyClean,
        });

        const k2 = await generateRSAKeyPair(2048);
        receiver = saveStoredWallet({
          name: 'Bob (Demo)',
          privateKeyPem: k2.privateKeyPem,
          publicKeyPem: k2.publicKeyPem,
          publicKeyClean: k2.publicKeyClean,
        });
        updateWalletCount();
      }

      handleSelectOriginWallet(sender);
      handleSelectDestWallet(receiver);
      handleField('monto', '50');

      // Auto-firmar
      const testData = {
        monto: 50,
        origen: sender.publicKeyClean,
        destino: receiver.publicKeyClean,
      };
      const signature = signDataWithForge(testData, sender.privateKeyPem);
      setSign(signature);

      toast.success('¡Transacción demo lista y firmada para enviar!', { id: toastId });
    } catch (err) {
      console.error(err);
      toast.error('Error en demo: ' + err.message, { id: toastId });
    }
  };

  const buildPayloadData = () => {
    const ori = stripPemHeaders(
      txType === 'PROPERTY' ? form.owner : form.origen
    );
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
      toast.error('Cargá o generá una clave privada para firmar.');
      return;
    }
    try {
      const data = buildPayloadData();
      const signature = signDataWithForge(data, privKeyContent);
      setSign(signature);
      toast.success('Documento firmado correctamente');
    } catch (err) {
      toast.error(err.message);
    }
  };

  const handleSubmit = async () => {
    if (!sign) {
      toast.error('Primero debes firmar la transacción.');
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

      toast.success('¡Transacción enviada con éxito!', { duration: 5000 });
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
    setOriginWalletName('');
    setDestWalletName('');
    setPrivKeyContent('');
    if (pubKeyInputRef.current) pubKeyInputRef.current.value = '';
    if (destPubKeyInputRef.current) destPubKeyInputRef.current.value = '';
    if (privKeyInputRef.current) privKeyInputRef.current.value = '';
  };

  const selectedType = TX_TYPES.find((t) => t.id === txType);

  return (
    <div className={styles.page}>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1e293b',
            color: '#fff',
            border: '1px solid #334155',
            fontSize: '14px',
            borderRadius: '10px',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#1e293b' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#1e293b' } },
        }}
      />

      {/* Modal de Billeteras y Generación RSA */}
      <WalletModal
        isOpen={isWalletModalOpen}
        onClose={() => setIsWalletModalOpen(false)}
        onSelectOrigin={handleSelectOriginWallet}
        onSelectDestination={handleSelectDestWallet}
        onWalletsChange={updateWalletCount}
      />

      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <h1 className={styles.title}>NUEVA TRANSACCIÓN</h1>
          <p className={styles.subtitle}>
            Firma RSA-SHA256 local y envío a la red UNLUCOIN
          </p>
        </div>
        <div className={styles.headerRight}>
          <button
            className={styles.demoFillBtn}
            onClick={handleQuickDemo}
            title="Llenar y firmar automáticamente con cuentas de prueba"
          >
            🧪 TEST RÁPIDO
          </button>
          <button
            className={styles.walletManagerBtn}
            onClick={() => setIsWalletModalOpen(true)}
          >
            🔑 BILLETERAS ({walletCount})
          </button>
          <div className={styles.blockCount}>
            <span className={styles.blockCountLabel}>NETWORK API</span>
            <span className={styles.blockCountVal}>{API_URL}</span>
          </div>
        </div>
      </div>

      <div className={styles.typeSelector}>
        {TX_TYPES.map((t) => (
          <button
            key={t.id}
            className={`${styles.typeBtn} ${txType === t.id ? styles.typeBtnActive : ''}`}
            style={txType === t.id ? { '--type-color': t.color } : {}}
            onClick={() => {
              setTxType(t.id);
              reset();
            }}
          >
            <span className={styles.typeIcon}>{t.icon}</span>
            <span className={styles.typeId}>{t.id}</span>
            <span className={styles.typeLabel}>{t.label}</span>
          </button>
        ))}
      </div>

      <div className={styles.formCard}>
        <div className={styles.formCardHeader}>
          <span
            className={styles.formCardIcon}
            style={{ color: selectedType.color }}
          >
            {selectedType.icon}
          </span>
          <span className={styles.formCardTitle}>
            Configuración de {txType}
          </span>
          <div
            className={styles.formCardLine}
            style={{ background: selectedType.color }}
          />
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
                onChange={(e) => handleField('monto', e.target.value)}
              />
            </Field>
          )}

          {(txType === 'PROPERTY' || txType === 'TX_NFT') && (
            <Field label="NFT ID" hint="Hash único del activo">
              <input
                className={styles.input}
                placeholder="ID del NFT"
                value={form.nft}
                onChange={(e) => handleField('nft', e.target.value)}
              />
            </Field>
          )}

          {/* ORIGEN / OWNER */}
          <Field
            label={txType === 'PROPERTY' ? 'DUEÑO (OWNER)' : 'ORIGEN'}
            hint={
              originWalletName ? (
                <span className={styles.accountBadge}>👤 {originWalletName}</span>
              ) : (
                'Clave pública del emisor'
              )
            }
          >
            <div className={styles.inputWithFile}>
              <input
                className={styles.input}
                placeholder="Pegar clave o generar una nueva..."
                value={
                  pubKeyFile
                    ? `Archivo: ${pubKeyFile}`
                    : txType === 'PROPERTY'
                    ? form.owner
                    : form.origen
                }
                onChange={(e) =>
                  handleField(
                    txType === 'PROPERTY' ? 'owner' : 'origen',
                    e.target.value
                  )
                }
              />
              <button
                type="button"
                className={styles.quickBtn}
                onClick={handleQuickGenerateOrigin}
                disabled={generatingOrigin}
                title="Generar un nuevo par de claves RSA al vuelo"
              >
                {generatingOrigin ? '⚡...' : '⚡ Generar'}
              </button>
              <button
                type="button"
                className={styles.quickBtn}
                onClick={() => setIsWalletModalOpen(true)}
                title="Seleccionar una cuenta guardada"
              >
                👤 Billeteras
              </button>
              <label className={styles.fileBtn}>
                📂 {pubKeyFile ? 'Cambiar' : 'Archivo'}
                <input
                  ref={pubKeyInputRef}
                  type="file"
                  accept=".pem,.pub,.key,.txt"
                  onChange={handlePubKeyFile}
                  hidden
                />
              </label>
            </div>
          </Field>

          {/* DESTINO */}
          {(txType === 'TX' || txType === 'TX_NFT') && (
            <Field
              label="DESTINO"
              hint={
                destWalletName ? (
                  <span className={styles.accountBadge} style={{ color: '#f0b429', borderColor: 'rgba(240,180,41,0.3)', background: 'rgba(240,180,41,0.1)' }}>
                    👤 {destWalletName}
                  </span>
                ) : (
                  'Clave pública del receptor'
                )
              }
            >
              <div className={styles.inputWithFile}>
                <input
                  className={styles.input}
                  placeholder="Pegar clave pública o seleccionar..."
                  value={
                    destPubKeyFile ? `Archivo: ${destPubKeyFile}` : form.destino
                  }
                  onChange={(e) => handleField('destino', e.target.value)}
                />
                <button
                  type="button"
                  className={styles.quickBtn}
                  onClick={handleQuickGenerateDest}
                  disabled={generatingDest}
                  title="Generar una clave de destino al vuelo"
                >
                  {generatingDest ? '⚡...' : '⚡ Generar'}
                </button>
                <button
                  type="button"
                  className={styles.quickBtn}
                  onClick={() => setIsWalletModalOpen(true)}
                  title="Seleccionar una cuenta guardada"
                >
                  👤 Billeteras
                </button>
                <label className={styles.fileBtn}>
                  📂 {destPubKeyFile ? 'Cambiar' : 'Archivo'}
                  <input
                    ref={destPubKeyInputRef}
                    type="file"
                    accept=".pem,.pub,.key,.txt"
                    onChange={handleDestPubKeyFile}
                    hidden
                  />
                </label>
              </div>
            </Field>
          )}

          <div className={styles.divider}>
            <span>SEGURIDAD & FIRMA RSA</span>
          </div>

          <Field
            label="CLAVE PRIVADA (RSA)"
            hint={
              privKeyContent
                ? '✔ Clave cargada y lista para firmar'
                : 'Se usa solo para firmar localmente en tu navegador'
            }
          >
            <div className={styles.inputWithFile}>
              <input
                className={styles.input}
                placeholder="Cargada automáticamente al elegir Origen o seleccioná archivo..."
                value={
                  privKeyFile
                    ? privKeyFile
                    : privKeyContent
                    ? '•••••••••••••••• (Clave privada en memoria)'
                    : ''
                }
                readOnly
              />
              <label
                className={styles.fileBtn}
                style={{
                  background: privKeyContent ? 'rgba(16, 185, 129, 0.15)' : 'rgba(0, 212, 255, 0.06)',
                  borderColor: privKeyContent ? '#10b981' : 'var(--border)',
                  color: privKeyContent ? '#10b981' : 'var(--accent-cyan)',
                }}
              >
                🔑 {privKeyContent ? 'Cargada ✔' : 'Cargar .pem'}
                <input
                  ref={privKeyInputRef}
                  type="file"
                  accept="*"
                  onChange={handlePrivKeyFile}
                  hidden
                />
              </label>
            </div>
          </Field>

          <Field
            label="FIRMA DIGITAL"
            hint="Resultado de la firma SHA256withRSA"
          >
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
          <button className={styles.resetBtn} onClick={reset}>
            ↺ LIMPIAR
          </button>
          <button
            className={styles.submitBtn}
            onClick={handleSubmit}
            disabled={loading || !sign}
          >
            {loading ? (
              <span className={styles.spinner} />
            ) : (
              <>⟶ ENVIAR TRANSACCIÓN</>
            )}
          </button>
        </div>

        <details className={styles.preview}>
          <summary className={styles.previewSummary}>
            Ver Payload Final (JSON)
          </summary>
          <pre className={styles.previewCode}>
            {JSON.stringify(
              {
                data: buildPayloadData(),
                type: txType,
                sign: sign,
              },
              null,
              2
            )}
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
