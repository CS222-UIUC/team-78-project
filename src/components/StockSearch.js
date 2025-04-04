import React, { useState } from "react";
import apiService from "../services/apiService";



const StockSearch = () => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query) return;
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/search?query=${query}`);
      const data = await response.json();
      console.log("API response:", data); // <-- ADD THIS
  
      setResults(data.stocks || []);
    } catch (error) {
      console.error("Error fetching stock data:", error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-lg mx-auto mt-10 p-4">
      <h2 className="text-xl font-bold mb-4">Stock Search</h2>
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Enter stock symbol..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="border p-2 w-full rounded-md"
        />
        <button
          onClick={handleSearch}
          disabled={loading}
          className="bg-blue-500 text-white px-4 py-2 rounded-md"
        >
          {loading ? "Searching..." : "Search"}
        </button>
      </div>
      <div>
        {results.length > 0 ? (
          results.map((stock) => (
            <div key={stock.symbol} className="border p-2 mb-2 rounded-md">
              <h3 className="font-bold">{stock.name} ({stock.symbol})</h3>
              <p>Price: ${stock.price}</p>
            </div>
          ))
        ) : (
          <p>No results found.</p>
        )}
      </div>
    </div>
  );
};

export default StockSearch;

// TODO: case insensitive search, dropdown - show a basic display of what the backend api is showing. refer to the figma ui. 