import { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [users, setUsers] = useState([]);
  const [wallets, setWallets] = useState([]);
  const [history, setHistory] = useState([]);
  const [userName, setUserName] = useState('');
  const [selectedUser, setSelectedUser] = useState('');
  const [amount, setAmount] = useState('');
  const [view, setView] = useState('main');
  const [toast, setToast] = useState(null);
  const [confirmDialog, setConfirmDialog] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    initDB();
  }, []);

  const query = async (sql) => {
    try {
      const res = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sql })
      });
      const data = await res.json();
      if (!data.success) {
        console.error('Query failed:', sql, 'Error:', data.error);
      }
      return data;
    } catch (error) {
      console.error('Request failed:', error);
      return { success: false, error: error.message };
    }
  };

  const initDB = async () => {
    await loadData();
  };

  const loadData = async () => {
    const u = await query('SELECT * FROM users');
    const w = await query('SELECT * FROM wallets');
    console.log('Wallets from backend:', w.result?.rows);
    if (u.success) setUsers(u.result.rows);
    if (w.success) {
      // Group wallets by user_id and keep only the latest active one
      const walletMap = {};
      w.result.rows.forEach(wallet => {
        const userId = wallet.user_id;
        if (!walletMap[userId] || wallet._version > (walletMap[userId]._version || 0)) {
          walletMap[userId] = wallet;
        }
      });
      const finalWallets = Object.values(walletMap);
      console.log('Final wallets to display:', finalWallets);
      setWallets(finalWallets);
    }
  };

  const createUser = async () => {
    if (!userName) return;
    const id = Date.now();
    const result = await query(`INSERT INTO users VALUES (${id}, '${userName}', '${userName.toLowerCase().replace(/\s+/g, '')}@example.com')`);
    if (result.success) {
      await query(`INSERT INTO wallets VALUES (${id}, ${id}, 0.0)`);
      setUserName('');
      await loadData();
      showToast('User created successfully!', 'success');
    } else {
      showToast('Error: ' + result.error, 'error');
    }
  };

  const credit = async () => {
    if (!selectedUser || !amount) return;
    const wallet = wallets.find(w => String(w.user_id) === String(selectedUser));
    if (!wallet) {
      showToast('Wallet not found', 'error');
      return;
    }
    const newBalance = parseFloat(wallet.balance) + parseFloat(amount);
    const result = await query(`UPDATE wallets SET balance = ${newBalance} WHERE wallet_id = ${wallet.wallet_id}`);
    if (result.success) {
      setAmount('');
      await loadData();
      showToast(`Credited $${amount}`, 'success');
    } else {
      showToast('Error: ' + result.error, 'error');
    }
  };

  const debit = async () => {
    if (!selectedUser || !amount) return;
    const wallet = wallets.find(w => String(w.user_id) === String(selectedUser));
    if (!wallet) {
      showToast('Wallet not found', 'error');
      return;
    }
    const newBalance = parseFloat(wallet.balance) - parseFloat(amount);
    if (newBalance < 0) {
      showToast('Insufficient balance', 'error');
      return;
    }
    const result = await query(`UPDATE wallets SET balance = ${newBalance} WHERE wallet_id = ${wallet.wallet_id}`);
    if (result.success) {
      setAmount('');
      await loadData();
      showToast(`Debited $${amount}`, 'success');
    } else {
      showToast('Error: ' + result.error, 'error');
    }
  };

  const deleteUser = async (userId) => {
    setConfirmDialog({
      message: 'Are you sure you want to delete this user?',
      onConfirm: async () => {
        setConfirmDialog(null);
        await query(`DELETE FROM wallets WHERE user_id = ${userId}`);
        await query(`DELETE FROM users WHERE id = ${userId}`);
        await loadData();
        showToast('User deleted successfully!', 'success');
      },
      onCancel: () => setConfirmDialog(null)
    });
  };

  const viewHistory = async (walletId) => {
    const h = await query(`SELECT * FROM wallets HISTORY WHERE wallet_id = ${walletId}`);
    if (h.success) {
      setHistory(h.result.rows);
      setView('history');
    }
  };

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-top"></div>
        <div className="loading-center">
          <h1 className="loading-title">
            <span className="ledger">LEDGER</span>
            <span className="db">DB</span>
            <br/>
            <span className="powered">POWERED BY </span>
            <span className="pesapal">PESAPAL</span>
          </h1>
          <button className="launch-btn" onClick={() => setIsLoading(false)}>Launch</button>
        </div>
        <div className="loading-bottom"></div>
      </div>
    );
  }

  return (
    <div className="app">
      {toast && (
        <div className={`toast ${toast.type}`}>
          {toast.message}
        </div>
      )}
      {confirmDialog && (
        <div className="modal-overlay">
          <div className="modal">
            <p>{confirmDialog.message}</p>
            <div className="modal-buttons">
              <button onClick={confirmDialog.onConfirm}>Yes</button>
              <button onClick={confirmDialog.onCancel}>Cancel</button>
            </div>
          </div>
        </div>
      )}
      <h1>💳 LedgerDB Wallet System</h1>
      
      {view === 'main' && (
        <>
          <div className="section">
            <h2>Create User</h2>
            <input value={userName} onChange={e => setUserName(e.target.value)} placeholder="Name" />
            <button onClick={createUser}>Create</button>
          </div>

          <div className="section">
            <h2>Wallets</h2>
            {wallets.map(w => {
              const user = users.find(u => String(u.id) === String(w.user_id));
              return (
                <div key={w.wallet_id} className="wallet">
                  <span>{user?.name || 'Unknown'}: ${parseFloat(w.balance).toFixed(2)}</span>
                  <button onClick={() => viewHistory(w.wallet_id)}>Audit Trail</button>
                  <button onClick={() => deleteUser(w.user_id)}>Delete</button>
                </div>
              );
            })}
          </div>

          <div className="section">
            <h2>Transaction</h2>
            <select value={selectedUser} onChange={e => setSelectedUser(e.target.value)}>
              <option value="">Select User</option>
              {users.map(u => <option key={u.id} value={u.id}>{u.name}</option>)}
            </select>
            <input type="number" value={amount} onChange={e => setAmount(e.target.value)} placeholder="Amount" />
            <button onClick={credit}>Credit</button>
            <button onClick={debit}>Debit</button>
          </div>
        </>
      )}

      {view === 'history' && (
        <div className="section">
          <h2>Audit Trail</h2>
          <button onClick={() => setView('main')}>Back</button>
          <table>
            <thead>
              <tr>
                <th>Version</th>
                <th>Balance</th>
                <th>Timestamp</th>
                <th>Active</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h, i) => (
                <tr key={i}>
                  <td>{h._version}</td>
                  <td>${h.balance.toFixed(2)}</td>
                  <td>{new Date(h._created_at).toLocaleString()}</td>
                  <td>{h._is_active ? '✓' : '✗'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;
