import { Link, useLocation } from 'react-router-dom';
import styles from './Navbar.module.css';

export default function Navbar() {
  const { pathname } = useLocation();

  return (
    <nav className={styles.nav}>
      <div className={styles.logo}>
        <span className={styles.logoIcon}>₿</span>
        <span className={styles.logoText}>UNLUCOIN</span>
        <span className={styles.logoBadge}>TESTNET</span>
      </div>
      <div className={styles.links}>
        <Link to="/" className={`${styles.link} ${pathname === '/' ? styles.active : ''}`}>
          <span className={styles.linkDot} />
          TRANSACCIONES
        </Link>
        <Link to="/blockchain" className={`${styles.link} ${pathname === '/blockchain' ? styles.active : ''}`}>
          <span className={styles.linkDot} />
          BLOCKCHAIN
        </Link>
      </div>
      <div className={styles.status}>
        <span className={styles.statusDot} />
        <span className={styles.statusText}>NODO ACTIVO</span>
      </div>
    </nav>
  );
}
