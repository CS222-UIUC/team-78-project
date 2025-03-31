import React, { useState } from 'react';

function App() {
  const [selectedStock, setSelectedStock] = useState(null);

  const handleStockSelection = (stock) => {
    setSelectedStock(stock);
  };

  return (
    <div className="bg-gray-100 min-h-screen">
      
      <main className="p-6">
        <h2>Select a Stock</h2>
        {/* filler stocks for now, once we use yFinance API we can fill that way */}
        <select onChange={(e) => handleStockSelection(e.target.value)}>
          <option value="">Select a Stock</option>
          <option value="AAPL">Apple (AAPL)</option>
          <option value="GOOG">Google (GOOG)</option>
          <option value="AMZN">Amazon (AMZN)</option>
        </select>

        <p>{selectedStock ? `You selected: ${selectedStock}` : 'No stock selected'}</p>
      </main>      
    </div>

  );
}

export default App;