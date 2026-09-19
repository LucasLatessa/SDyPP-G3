import forge from 'node-forge';

const STORAGE_KEY = 'unlucoin_wallets';

/**
 * Limpia cabeceras PEM y espacios en blanco de una clave
 */
export const stripPemHeaders = (pemString) => {
  if (!pemString) return '';
  return pemString
    .replace(/-----BEGIN [^-]+-----/, '')
    .replace(/-----END [^-]+-----/, '')
    .replace(/\s+/g, '');
};

/**
 * Serialización determinista de objetos JSON (claves ordenadas)
 */
export const deterministicStringify = (obj) => {
  const sortedKeys = Object.keys(obj).sort();
  const sortedObj = {};
  sortedKeys.forEach((key) => {
    sortedObj[key] = obj[key];
  });
  return JSON.stringify(sortedObj);
};

/**
 * Firma digitalmente un objeto JSON usando una clave privada RSA (SHA256 + PKCS#1 v1.5)
 */
export const signDataWithForge = (dataToSign, privateKeyPem) => {
  try {
    const dataString = deterministicStringify(dataToSign);
    let pemToParse = privateKeyPem.trim();

    if (!pemToParse.includes('-----BEGIN')) {
      const formatBase64 = (str) => str.match(/.{1,64}/g).join('\n');
      pemToParse = `-----BEGIN RSA PRIVATE KEY-----\n${formatBase64(
        pemToParse.replace(/\s+/g, '')
      )}\n-----END RSA PRIVATE KEY-----`;
    }

    const privateKey = forge.pki.privateKeyFromPem(pemToParse);
    const md = forge.md.sha256.create();
    md.update(dataString, 'utf8');
    const signature = privateKey.sign(md);

    return forge.util.encode64(signature);
  } catch (error) {
    console.error('Error al procesar la firma:', error);
    throw new Error('Clave privada inválida. Verificá el formato RSA-PEM.');
  }
};

/**
 * Genera de forma asíncrona un par de claves RSA (por defecto 2048 bits)
 * utilizando Web Workers en background para no bloquear la UI.
 */
export const generateRSAKeyPair = (bits = 2048) => {
  return new Promise((resolve, reject) => {
    forge.pki.rsa.generateKeyPair({ bits, workers: -1 }, (err, keypair) => {
      if (err) {
        return reject(err);
      }
      try {
        const privateKeyPem = forge.pki.privateKeyToPem(keypair.privateKey);
        const publicKeyPem = forge.pki.publicKeyToPem(keypair.publicKey);
        const publicKeyClean = stripPemHeaders(publicKeyPem);

        resolve({
          privateKeyPem,
          publicKeyPem,
          publicKeyClean,
          bits,
          createdAt: new Date().toISOString(),
        });
      } catch (err2) {
        reject(err2);
      }
    });
  });
};

/**
 * Descarga una cadena de texto como archivo en el navegador
 */
export const downloadFile = (filename, content, mimeType = 'text/plain') => {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Obtiene todas las cuentas guardadas en localStorage
 */
export const getStoredWallets = () => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch (e) {
    console.error('Error al leer billeteras de localStorage:', e);
    return [];
  }
};

/**
 * Guarda una nueva billetera en localStorage
 */
export const saveStoredWallet = ({ name, privateKeyPem, publicKeyPem, publicKeyClean }) => {
  const wallets = getStoredWallets();
  const id = `wallet_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
  const newWallet = {
    id,
    name: name?.trim() || `Billetera #${wallets.length + 1}`,
    privateKeyPem,
    publicKeyPem,
    publicKeyClean: publicKeyClean || stripPemHeaders(publicKeyPem),
    createdAt: new Date().toISOString(),
  };

  const updated = [newWallet, ...wallets];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  return newWallet;
};

/**
 * Elimina una billetera de localStorage por ID
 */
export const deleteStoredWallet = (id) => {
  const wallets = getStoredWallets();
  const filtered = wallets.filter((w) => w.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  return filtered;
};
