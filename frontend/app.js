const status = document.querySelector('#status');
const button = document.querySelector('#check-connection');

async function checkConnection() {
  button.disabled = true;
  status.textContent = 'Checking connection…';
  status.dataset.state = 'loading';
  try {
    const response = await fetch('/api/health', {
      signal: AbortSignal.timeout(5000),
      cache: 'no-store',
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    if (data.status !== 'ok') throw new Error('Unexpected API response');
    status.textContent = data.message;
    status.dataset.state = 'success';
  } catch {
    status.textContent = 'Unable to reach the backend. Make sure the server is running, then try again.';
    status.dataset.state = 'error';
  } finally {
    button.disabled = false;
  }
}
button.addEventListener('click', checkConnection);
checkConnection();
