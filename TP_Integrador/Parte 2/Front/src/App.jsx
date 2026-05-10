import { useState } from 'react';
import forge from 'node-forge';
import toast, { Toaster } from 'react-hot-toast';

function App() {
  const [txType, setTxType] = useState('TX');
  const [formData, setFormData] = useState({});
  const [pubKeyFile, setPubKeyFile] = useState(null);
  const [destPubKeyFile, setDestPubKeyFile] = useState(null); // Nuevo estado para el destino
  const [privKeyFile, setPrivKeyFile] = useState(null);

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e, setFileState) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setFileState(event.target.result);
      };
      reader.readAsText(file);
    }
  };

  const stripPemHeaders = (pemString) => {
    if (!pemString) return "";
    return pemString
      .replace(/-----BEGIN [^-]+-----/, '')
      .replace(/-----END [^-]+-----/, '')
      .replace(/\s+/g, '');
  };

  const signData = (dataToSign, privateKeyPem) => {
    try {
      const deterministicStringify = (obj) => {
        const sortedKeys = Object.keys(obj).sort();
        const sortedObj = {};
        sortedKeys.forEach(key => { sortedObj[key] = obj[key]; });
        return JSON.stringify(sortedObj);
      };

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
      throw new Error("Clave privada inválida. Verificá que sea RSA-4096 en formato PEM.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!privKeyFile) {
      toast.error("Se requiere la clave privada para firmar.");
      return;
    }

    // Limpiamos la clave pública de origen (archivo o input manual)
    const cleanPubKey = pubKeyFile ? stripPemHeaders(pubKeyFile) : stripPemHeaders(formData.origen);
    
    // Limpiamos la clave pública de destino (archivo o input manual)
    const cleanDestPubKey = destPubKeyFile ? stripPemHeaders(destPubKeyFile) : stripPemHeaders(formData.destino);
    
    let payloadData = {};
    
    if (txType === 'TX') {
      if (!cleanDestPubKey) return toast.error("Falta la clave pública del destino.");
      payloadData = {
        monto: Number(formData.monto),
        origen: cleanPubKey,
        destino: cleanDestPubKey
      };
    } else if (txType === 'PROPERTY') {
      payloadData = {
        nft: formData.nft,
        owner: cleanPubKey
      };
    } else if (txType === 'TX_NFT') {
      if (!cleanDestPubKey) return toast.error("Falta la clave pública del destino.");
      payloadData = {
        nft: formData.nft,
        origen: cleanPubKey,
        destino: cleanDestPubKey
      };
    }

    const loadingToast = toast.loading('Enviando transacción a la red...');

    try {
      const signature = signData(payloadData, privKeyFile);

      const finalPayload = {
        data: payloadData,
        type: txType,
        sign: signature
      };

      const response = await fetch(import.meta.env.VITE_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(finalPayload),
      });
      
      const resultText = await response.text();
      toast.dismiss(loadingToast);

      if (response.ok) {
        toast.success(resultText, { duration: 4000 });
        
        // Reset del formulario
        e.target.reset();
        setPrivKeyFile(null);
        setPubKeyFile(null);
        setDestPubKeyFile(null); // Reseteamos el nuevo estado
        setFormData({});
      } else {
        try {
          const errorJson = JSON.parse(resultText);
          toast.error(errorJson.error, { duration: 5000 });
        } catch {
          toast.error(resultText, { duration: 5000 });
        }
      }
      
    } catch (error) {
      toast.dismiss(loadingToast);
      toast.error(error.message || "Error de conexión con el servidor.", { duration: 5000 });
    }
  };

  // Función auxiliar para resetear los inputs al cambiar de tipo de transacción
  const handleTypeChange = (type) => {
    setTxType(type); 
    setFormData({}); 
    setPubKeyFile(null);
    setDestPubKeyFile(null);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center py-10 px-4">
      
      <Toaster 
        position="bottom-center"
        toastOptions={{
          style: { background: '#1e293b', color: '#fff', border: '1px solid #334155' },
          success: { iconTheme: { primary: '#10b981', secondary: '#1e293b' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#1e293b' } },
        }}
      />

      <h1 className="text-5xl font-bold text-emerald-400 mb-8 tracking-wider">UNLUCOIN</h1>
      
      <div className="bg-slate-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-slate-700">
        <div className="flex gap-2 mb-6">
          {['TX', 'PROPERTY', 'TX_NFT'].map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => handleTypeChange(type)}
              className={`flex-1 py-2 rounded font-semibold transition-all ${txType === type ? 'bg-emerald-500 text-slate-900 scale-105' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              {type}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          
          {/* Inputs base */}
          {txType === 'TX' && (
            <input type="number" name="monto" placeholder="Monto" onChange={handleInputChange} className="p-3 rounded bg-slate-900 border border-slate-600 focus:border-emerald-500 outline-none" required />
          )}

          {(txType === 'PROPERTY' || txType === 'TX_NFT') && (
            <input type="text" name="nft" placeholder="ID del NFT" onChange={handleInputChange} className="p-3 rounded bg-slate-900 border border-slate-600 focus:border-emerald-500 outline-none" required />
          )}

          {/* Bloque: Origen */}
          <div className="flex flex-col gap-2 p-3 bg-slate-900/50 rounded border border-slate-700">
            <span className="text-sm font-bold text-slate-300">Emisor / Origen</span>
            <input type="text" name="origen" placeholder="Pegar clave pública o..." onChange={handleInputChange} className="p-2 text-sm rounded bg-slate-800 border border-slate-600 focus:border-emerald-500 outline-none" disabled={pubKeyFile !== null} />
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">O subir archivo:</span>
              <input type="file" accept=".pub,.pem,.txt" onChange={(e) => handleFileChange(e, setPubKeyFile)} className="text-xs file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:bg-emerald-500/20 file:text-emerald-400 hover:file:bg-emerald-500/30" />
            </div>
          </div>

          {/* Bloque: Destino (Solo para TX y TX_NFT) */}
          {(txType === 'TX' || txType === 'TX_NFT') && (
            <div className="flex flex-col gap-2 p-3 bg-slate-900/50 rounded border border-slate-700">
              <span className="text-sm font-bold text-slate-300">Receptor / Destino</span>
              <input type="text" name="destino" placeholder="Pegar clave pública o..." onChange={handleInputChange} className="p-2 text-sm rounded bg-slate-800 border border-slate-600 focus:border-emerald-500 outline-none" disabled={destPubKeyFile !== null} />
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500">O subir archivo:</span>
                <input type="file" accept=".pub,.pem,.txt" onChange={(e) => handleFileChange(e, setDestPubKeyFile)} className="text-xs file:mr-2 file:py-1 file:px-2 file:rounded file:border-0 file:bg-emerald-500/20 file:text-emerald-400 hover:file:bg-emerald-500/30" />
              </div>
            </div>
          )}

          {/* Bloque: Firma (Privada) */}
          <div className="flex flex-col gap-2 mt-4 p-4 border-2 border-dashed border-emerald-500/30 rounded bg-emerald-500/5 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-slate-800 px-2 text-xs font-bold text-emerald-400">FIRMA ELECTRÓNICA</div>
            <p className="text-[10px] text-slate-400 text-center leading-tight">Seleccioná tu archivo de clave privada (RSA-4096) para firmar localmente. <br/> La clave no se transmite a la red.</p>
            <input type="file" accept=".pem,.key,.txt" onChange={(e) => handleFileChange(e, setPrivKeyFile)} className="mx-auto mt-2 text-sm text-slate-300 file:cursor-pointer file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-emerald-500 file:text-slate-900 hover:file:bg-emerald-400 font-semibold" required />
          </div>

          <button type="submit" className="mt-4 w-full py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-black rounded shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all active:scale-[0.98]">
            FIRMAR Y ENVIAR A LA RED
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;