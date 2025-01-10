async function runScraper() {
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    loading.style.display = 'block';
    results.innerHTML = '';
    
    try {
        const response = await fetch('/run_scraper');
        const data = await response.json();
        
        if (data.success) {
            const record = data.data;
            const date = new Date(record.timestamp.$date);
            
            let html = `
                <h2>These are the most happening topics as on ${date.toLocaleString()}</h2>
                <ul>
                    <li>${record.nameoftrend1}</li>
                    <li>${record.nameoftrend2}</li>
                    <li>${record.nameoftrend3}</li>
                    <li>${record.nameoftrend4}</li>
                    <li>${record.nameoftrend5}</li>
                </ul>
                <p>The IP address used for this query was ${record.ip_address}</p>
                <h3>JSON extract from MongoDB:</h3>
                <pre>${JSON.stringify(record, null, 2)}</pre>
            `;
            
            results.innerHTML = html;
        } else {
            results.innerHTML = `<p style="color: red">Error: ${data.error}</p>`;
        }
    } catch (error) {
        results.innerHTML = `<p style="color: red">Error: ${error.message}</p>`;
    } finally {
        loading.style.display = 'none';
    }
}