import express from 'express';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

app.use(express.json());
app.use(express.static('dist')); // Serve built files

// PDF generation endpoint
app.post('/api/generate-pdf', async (req, res) => {
    const { week } = req.body;

    if (!week) {
        return res.status(400).json({ error: 'Week parameter is required' });
    }

    try {
        console.log(`Generating PDF for week ${week}...`);

        // Run the existing PDF export script
        const child = spawn('node', ['scripts/export-pdf.mjs', '--week', week], {
            cwd: __dirname,
            stdio: 'pipe'
        });

        let output = '';
        let error = '';

        child.stdout.on('data', (data) => {
            output += data.toString();
            console.log('PDF Script Output:', data.toString());
        });

        child.stderr.on('data', (data) => {
            error += data.toString();
            console.error('PDF Script Error:', data.toString());
        });

        child.on('close', (code) => {
            if (code === 0) {
                // PDF generated successfully, send the file
                const pdfPath = path.join(__dirname, 'pdf-exports', `week${week.padStart(2, '0')}.pdf`);

                if (fs.existsSync(pdfPath)) {
                    res.setHeader('Content-Type', 'application/pdf');
                    res.setHeader('Content-Disposition', `attachment; filename="week${week}.pdf"`);

                    const fileStream = fs.createReadStream(pdfPath);
                    fileStream.pipe(res);

                    fileStream.on('end', () => {
                        // Optionally delete the file after sending
                        // fs.unlinkSync(pdfPath);
                    });
                } else {
                    res.status(500).json({ error: 'PDF file not found after generation' });
                }
            } else {
                console.error(`PDF generation failed with code ${code}`);
                console.error('Error output:', error);
                res.status(500).json({
                    error: 'PDF generation failed',
                    details: error || 'Unknown error'
                });
            }
        });

        child.on('error', (err) => {
            console.error('Failed to start PDF generation process:', err);
            res.status(500).json({ error: 'Failed to start PDF generation process' });
        });

    } catch (error) {
        console.error('PDF generation error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Catch all handler: serve index.html for any non-API routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Access the application at: http://localhost:${PORT}`);
});