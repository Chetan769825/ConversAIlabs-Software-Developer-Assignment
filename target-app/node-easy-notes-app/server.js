const express = require('express');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const dbConfig = require('./config/database.config.js');

const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

app.get('/', (_req, res) => {
    res.json({ message: 'Welcome to EasyNotes application. Take notes quickly. Organize and keep track of all your notes.' });
});
require('./app/routes/note.routes.js')(app);

async function start() {
    await mongoose.connect(dbConfig.url);
    console.log('Successfully connected to the database');
    const port = process.env.PORT || 3000;
    return app.listen(port, () => console.log(`Server is listening on port ${port}`));
}

if (require.main === module) {
    start().catch(error => {
        console.error('Could not connect to the database. Exiting now...', error.message);
        process.exitCode = 1;
    });
}

module.exports = { app, start };
