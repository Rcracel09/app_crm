import { useState, useEffect } from 'react'
import './App.css'

interface Customer {
  id: number
  name: string
  email: string
  phone: string
  address: string
  company: string
  notes: string
  created_at: string
}

interface Interaction {
  id: number
  customer_name: string
  interaction_type: string
  subject: string
  description: string
  created_by: string
  created_at: string
}

interface Stats {
  total_customers: number
  total_interactions: number
  pt_emails: number
}

function App() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [interactions, setInteractions] = useState<Interaction[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      
      // Fetch stats
      const statsRes = await fetch('/api/stats')
      const statsData = await statsRes.json()
      setStats(statsData)
      
      // Fetch customers
      const customersRes = await fetch('/api/customers')
      const customersData = await customersRes.json()
      setCustomers(customersData.customers)
      
      // Fetch interactions
      const interactionsRes = await fetch('/api/interactions')
      const interactionsData = await interactionsRes.json()
      setInteractions(interactionsData.interactions)
      
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
      setLoading(false)
    }
  }

  const getInteractionTypeClass = (type: string) => {
    const classes: { [key: string]: string } = {
      email: 'type-email',
      call: 'type-call',
      meeting: 'type-meeting',
      support: 'type-support'
    }
    return classes[type] || ''
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <h2>Loading CRM data...</h2>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container">
        <div className="error">
          <h2>Error loading data</h2>
          <p>{error}</p>
          <button onClick={fetchData}>Retry</button>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <header className="header">
        <h1>🏢 CRM App</h1>
        <p className="subtitle">Customer Relationship Management - LTPLabs E-Catalog</p>
      </header>

      <div className="warning">
        <span className="warning-icon">⚠️</span>
        <span className="warning-text">
          DADOS DE DEMONSTRAÇÃO - Contém PII fictícia para testes de anonimização
        </span>
      </div>

      {stats && (
        <div className="stats">
          <div className="stat-card">
            <div className="stat-number">{stats.total_customers}</div>
            <div className="stat-label">Total Clientes</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.total_interactions}</div>
            <div className="stat-label">Interações</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.pt_emails}</div>
            <div className="stat-label">Emails .pt</div>
          </div>
        </div>
      )}

      <section className="section">
        <h2>📊 Customers</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Company</th>
                <th>Address</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td>{customer.id}</td>
                  <td><span className="pii-field">{customer.name}</span></td>
                  <td><span className="pii-field">{customer.email}</span></td>
                  <td><span className="pii-field">{customer.phone}</span></td>
                  <td>{customer.company}</td>
                  <td><pre className="address">{customer.address}</pre></td>
                  <td><pre className="notes">{customer.notes}</pre></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="section">
        <h2>💬 Interactions</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Customer</th>
                <th>Type</th>
                <th>Subject</th>
                <th>Description</th>
                <th>Created By</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {interactions.map((interaction) => (
                <tr key={interaction.id}>
                  <td>{interaction.id}</td>
                  <td>{interaction.customer_name}</td>
                  <td>
                    <span className={`interaction-type ${getInteractionTypeClass(interaction.interaction_type)}`}>
                      {interaction.interaction_type}
                    </span>
                  </td>
                  <td>{interaction.subject}</td>
                  <td><pre className="description">{interaction.description}</pre></td>
                  <td><span className="pii-field">{interaction.created_by}</span></td>
                  <td>{new Date(interaction.created_at).toLocaleString('pt-PT')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <footer className="footer">
        <p><strong>CRM App v1.0</strong></p>
        <p>LTPLabs E-Catalog Demo Application</p>
        <p>🔒 Dados fictícios para demonstração de anonimização</p>
      </footer>
    </div>
  )
}

export default App