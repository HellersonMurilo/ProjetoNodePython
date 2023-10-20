const express = require('express');
const { spawn } = require('child_process');
const app = express();
const port = 3000;

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>Executar Script Python</title>
      </head>
      <body>
      <h1>Ola Bruno, esta dando certo :)</h1>
        <h1>Executar Script Python</h1>
        <form action="/executar-python" method="post">
          <button type="submit">Executar Script Python</button>
        </form>
      </body>
    </html>
  `);
});

app.post('/executar-python', (req, res) => {
  const pythonProcess = spawn('python', ['ROBOv10.py'], {
    stdio: 'inherit',
  });

  pythonProcess.on('exit', (code, signal) => {
    if (code === 0) {
      res.send('Script Python executado com sucesso!');
    } else {
      res.status(500).send('Erro ao executar o script Python.');
    }
  });
});

app.listen(port, () => {
  console.log(`Servidor Node.js rodando em http://localhost:${port}`);
});
