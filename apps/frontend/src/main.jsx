import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return <main>
    <h1>GKE GitOps Shop</h1>
    <p>Starter frontend for the Product API and Order API.</p>
    <section><h2>Products</h2><p>Sample catalog is served by the Product API.</p>
      <a href="/api/products">Open Product API route (configure proxy/routing in a later lab)</a>
    </section>
    <section><h2>Orders</h2><p>Use the Order API Swagger UI at <code>/docs</code> on its internal service during development.</p></section>
  </main>;
}
createRoot(document.getElementById('root')).render(<App />);
