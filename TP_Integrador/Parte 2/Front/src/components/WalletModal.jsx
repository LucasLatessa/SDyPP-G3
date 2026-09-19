import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  generateRSAKeyPair,
  downloadFile,
  getStoredWallets,
  saveStoredWallet,
  deleteStoredWallet,
} from '../utils/crypto';
import styles from './WalletModal.module.css';

export default function WalletModal({
  isOpen,
  onClose,
  onSelectOrigin,
  onSelectDestination,
  onWalletsChange,
}) {
  const [activeTab, setActiveTab] = useState('generate'); // 'generate' | 'list'
  const [walletName, setWalletName] = useState('');
  const [keyBits, setKeyBits] = useState(2048);
  const [generating, setGenerating] = useState(false);
  const [generatedKey, setGeneratedKey] = useState(null);
  const [savedWallets, setSavedWallets] = useState([]);

  useEffect(() => {
    if (isOpen) {
      loadWallets();
    }
  }, [isOpen]);

  const loadWallets = () => {
    const list = getStoredWallets();
    setSavedWallets(list);
  };

  if (!isOpen) return null;

  const handleGenerate = async () => {
    setGenerating(true);
    const toastId = toast.loading(`Generando claves RSA de ${keyBits} bits...`);
    try {
      // Small timeout to allow render of loading state
      await new Promise((r) => setTimeout(r, 50));
      const keypair = await generateRSAKeyPair(keyBits);
      setGeneratedKey(keypair);
      toast.success('¡Par de claves RSA generado exitosamente!', { id: toastId });
    } catch (err) {
      console.error(err);
      toast.error('Error al generar las claves: ' + err.message, { id: toastId });
    } finally {
      setGenerating(false);
    }
  };

  const handleSaveToWallets = () => {
    if (!generatedKey) return;
    const name = walletName.trim() || `Billetera #${savedWallets.length + 1}`;
    const newWallet = saveStoredWallet({
      name,
      privateKeyPem: generatedKey.privateKeyPem,
      publicKeyPem: generatedKey.publicKeyPem,
      publicKeyClean: generatedKey.publicKeyClean,
    });
    loadWallets();
    if (onWalletsChange) onWalletsChange();
    toast.success(`Cuenta "${name}" guardada localmente`);
    setWalletName('');
  };

  const handleDeleteWallet = (id, name) => {
    const updated = deleteStoredWallet(id);
    setSavedWallets(updated);
    if (onWalletsChange) onWalletsChange();
    toast.success(`Cuenta "${name}" eliminada`);
  };

  const copyToClipboard = (text, label) => {
    navigator.clipboard.writeText(text);
    toast.success(`${label} copiada al portapapeles`);
  };

  const handleDownloadKeys = (walletOrKey, namePrefix = 'unlucoin') => {
    const safeName = (walletOrKey.name || namePrefix).toLowerCase().replace(/\s+/g, '_');
    // Descargar Clave Pública
    downloadFile(`${safeName}.pub`, walletOrKey.publicKeyPem || walletOrKey.publicKeyClean);
    // Descargar Clave Privada
    downloadFile(`${safeName}.pem`, walletOrKey.privateKeyPem);
    toast.success('Archivos .pub y .pem descargados');
  };

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <div className={styles.headerTitle}>
            <span>🔑</span>
            <span>GESTOR DE CLAVES Y BILLETERAS</span>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>
            ✕
          </button>
        </div>

        <div className={styles.tabs}>
          <button
            className={`${styles.tab} ${activeTab === 'generate' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('generate')}
          >
            ⚡ GENERADOR RSA
          </button>
          <button
            className={`${styles.tab} ${activeTab === 'list' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('list')}
          >
            📁 CUENTAS GUARDADAS ({savedWallets.length})
          </button>
        </div>

        <div className={styles.content}>
          {activeTab === 'generate' && (
            <>
              <div className={styles.field}>
                <label className={styles.label}>
                  <span>ALIAS / NOMBRE DE LA CUENTA (OPCIONAL)</span>
                </label>
                <input
                  className={styles.input}
                  placeholder="Ej: Billetera Alicia, Nodo Validador..."
                  value={walletName}
                  onChange={(e) => setWalletName(e.target.value)}
                />
              </div>

              <div className={styles.field}>
                <label className={styles.label}>
                  <span>LONGITUD DE CLAVE RSA</span>
                  <span style={{ color: '#64748b' }}>2048 bits es el estándar óptimo</span>
                </label>
                <div style={{ display: 'flex', gap: '10px' }}>
                  {[1024, 2048, 4096].map((bits) => (
                    <button
                      key={bits}
                      type="button"
                      className={styles.miniBtn}
                      style={{
                        flex: 1,
                        padding: '8px',
                        borderColor: keyBits === bits ? '#00d4ff' : '#334155',
                        color: keyBits === bits ? '#00d4ff' : '#94a3b8',
                        background: keyBits === bits ? 'rgba(0, 212, 255, 0.1)' : 'transparent',
                      }}
                      onClick={() => setKeyBits(bits)}
                    >
                      {bits} bits {bits === 2048 ? '★' : ''}
                    </button>
                  ))}
                </div>
              </div>

              <button
                className={styles.generateBtn}
                onClick={handleGenerate}
                disabled={generating}
              >
                {generating ? (
                  <>
                    <span className={styles.spinner} />
                    GENERANDO PAR DE CLAVES...
                  </>
                ) : (
                  <>⚡ GENERAR NUEVO PAR DE CLAVES RSA</>
                )}
              </button>

              {generatedKey && (
                <>
                  <div className={styles.keyBox}>
                    <div className={styles.keyBoxHeader}>
                      <span className={styles.keyBoxTitle}>CLAVE PÚBLICA (PUBLIC KEY)</span>
                      <div className={styles.keyBoxActions}>
                        <button
                          className={styles.miniBtn}
                          onClick={() => copyToClipboard(generatedKey.publicKeyClean, 'Clave Pública')}
                        >
                          📋 Copiar
                        </button>
                        <button
                          className={styles.miniBtn}
                          onClick={() =>
                            downloadFile(
                              `${walletName.trim() || 'unlucoin'}.pub`,
                              generatedKey.publicKeyPem
                            )
                          }
                        >
                          ⬇ .pub
                        </button>
                      </div>
                    </div>
                    <pre className={styles.keyPreview}>{generatedKey.publicKeyClean}</pre>
                  </div>

                  <div className={styles.keyBox}>
                    <div className={styles.keyBoxHeader}>
                      <span className={styles.keyBoxTitle} style={{ color: '#10b981' }}>
                        CLAVE PRIVADA (PRIVATE KEY)
                      </span>
                      <div className={styles.keyBoxActions}>
                        <button
                          className={styles.miniBtn}
                          onClick={() => copyToClipboard(generatedKey.privateKeyPem, 'Clave Privada')}
                        >
                          📋 Copiar
                        </button>
                        <button
                          className={styles.miniBtn}
                          onClick={() =>
                            downloadFile(
                              `${walletName.trim() || 'unlucoin'}.pem`,
                              generatedKey.privateKeyPem
                            )
                          }
                        >
                          ⬇ .pem
                        </button>
                      </div>
                    </div>
                    <pre className={styles.keyPreview} style={{ color: '#10b981' }}>
                      {generatedKey.privateKeyPem}
                    </pre>
                  </div>

                  <div className={styles.saveActions}>
                    <button className={styles.saveBtn} onClick={handleSaveToWallets}>
                      💾 GUARDAR EN MIS CUENTAS
                    </button>
                    <button
                      className={styles.useBtn}
                      onClick={() => {
                        if (onSelectOrigin) {
                          onSelectOrigin({
                            name: walletName || 'Clave Generada',
                            publicKeyClean: generatedKey.publicKeyClean,
                            privateKeyPem: generatedKey.privateKeyPem,
                          });
                        }
                        onClose();
                        toast.success('Claves aplicadas como ORIGEN y listas para firmar');
                      }}
                    >
                      🚀 USAR DIRECTO COMO ORIGEN
                    </button>
                  </div>
                </>
              )}
            </>
          )}

          {activeTab === 'list' && (
            <div className={styles.walletsList}>
              {savedWallets.length === 0 ? (
                <div className={styles.emptyState}>
                  <span className={styles.emptyIcon}>📭</span>
                  <p>No tienes cuentas guardadas en el navegador.</p>
                  <button
                    className={styles.miniBtn}
                    style={{ padding: '8px 16px', color: '#00d4ff', borderColor: '#00d4ff' }}
                    onClick={() => setActiveTab('generate')}
                  >
                    Generar una nueva cuenta
                  </button>
                </div>
              ) : (
                savedWallets.map((w) => (
                  <div key={w.id} className={styles.walletCard}>
                    <div className={styles.walletCardHeader}>
                      <span className={styles.walletCardTitle}>
                        <span>👤</span>
                        {w.name}
                      </span>
                      <span className={styles.walletDate}>
                        {new Date(w.createdAt).toLocaleDateString()}
                      </span>
                    </div>

                    <div className={styles.walletKeyPreview}>
                      <span className={styles.walletKeyText}>{w.publicKeyClean}</span>
                      <button
                        className={styles.miniBtn}
                        onClick={() => copyToClipboard(w.publicKeyClean, 'Clave Pública')}
                        title="Copiar Clave Pública"
                      >
                        📋
                      </button>
                    </div>

                    <div className={styles.walletActions}>
                      <div className={styles.applyGroup}>
                        {onSelectOrigin && (
                          <button
                            className={`${styles.applyBtn} ${styles.applyOriginBtn}`}
                            onClick={() => {
                              onSelectOrigin(w);
                              onClose();
                              toast.success(`"${w.name}" seleccionada como ORIGEN`);
                            }}
                          >
                            ⤑ ORIGEN
                          </button>
                        )}
                        {onSelectDestination && (
                          <button
                            className={`${styles.applyBtn} ${styles.applyDestBtn}`}
                            onClick={() => {
                              onSelectDestination(w);
                              onClose();
                              toast.success(`"${w.name}" seleccionada como DESTINO`);
                            }}
                          >
                            DESTINO ⤥
                          </button>
                        )}
                      </div>

                      <div style={{ display: 'flex', gap: '6px' }}>
                        <button
                          className={styles.miniBtn}
                          onClick={() => handleDownloadKeys(w)}
                          title="Descargar archivos .pem y .pub"
                        >
                          ⬇ Descargar
                        </button>
                        <button
                          className={styles.deleteBtn}
                          onClick={() => handleDeleteWallet(w.id, w.name)}
                          title="Eliminar de almacenamiento local"
                        >
                          🗑
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
