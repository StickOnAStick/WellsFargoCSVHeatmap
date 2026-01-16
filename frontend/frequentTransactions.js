

async function renderFrequentTransactions() {
  let data;
  try {
    const res = await fetch("./frequent-transactions.json")
    if(!res.ok) throw new Error(`HTTP ${res.status}`);
    data = await res.json();
  } catch(err) {
    console.error("Failed to load frequent-transactions.json", err);
    return;
  }

  frequent_transactions = 


}