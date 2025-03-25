const searchStock = async (query) => {
    const response = await fetch(`/api/search?query=${query}`);
    return response.json();
  };
  
  export default { searchStock };
  