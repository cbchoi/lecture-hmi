#!/usr/bin/env node

import { program } from 'commander';
import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

program
  .name('export-pdf')
  .description('Export reveal.js presentations to PDF')
  .option('-w, --week <week>', 'Export specific week (e.g., 03)')
  .option('-a, --all', 'Export all available weeks')
  .option('-o, --output <dir>', 'Output directory', 'pdf-exports')
  .option('-p, --port <port>', 'Development server port', '5173')
  .option('--width <width>', 'Slide width', '1920')
  .option('--height <height>', 'Slide height', '1080')
  .parse();

const options = program.opts();

async function exportWeekToPDF(week, outputDir, serverPort, width = 1920, height = 1080) {
  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--font-render-hinting=none',
      '--disable-font-subpixel-positioning',
      '--disable-features=VizDisplayCompositor',
      '--disable-audio-output',
      '--disable-dev-shm-usage',
      '--no-first-run',
      '--no-zygote',
      '--disable-software-rasterizer'
    ]
  });

  try {
    const page = await browser.newPage();
    await page.setViewport({ width: parseInt(width), height: parseInt(height) });

    const url = `http://localhost:${serverPort}?week=${week}&print-pdf`;
    console.log(`Loading week ${week} from ${url}...`);

    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // Wait for reveal.js to fully initialize
    await page.waitForSelector('.reveal .slides section', { timeout: 10000 });

    // Wait for fonts to load (especially Korean fonts)
    await page.evaluate(() => {
      return document.fonts.ready;
    });

    // Wait a bit more to ensure all content and fonts are loaded
    await new Promise(resolve => setTimeout(resolve, 3000));

    const outputPath = join(outputDir, `week${week.padStart(2, '0')}.pdf`);

    await page.pdf({
      path: outputPath,
      format: 'A4',
      landscape: true,
      printBackground: true,
      margin: {
        top: '10mm',
        bottom: '10mm',
        left: '10mm',
        right: '10mm'
      }
    });

    console.log(`✓ Exported Week ${week} to ${outputPath}`);
    return true;
  } catch (error) {
    console.error(`✗ Failed to export Week ${week}:`, error.message);
    return false;
  } finally {
    await browser.close();
  }
}

async function getAvailableWeeks() {
  const slidesDir = join(__dirname, '..', 'slides');
  try {
    const files = await fs.readdir(slidesDir);
    return files
      .filter(file => file.match(/^week\d{2}-/))
      .map(file => file.match(/week(\d{2})-/)[1])
      .sort();
  } catch (error) {
    console.warn('Could not read slides directory, using default weeks 01-13');
    return Array.from({ length: 13 }, (_, i) => (i + 1).toString().padStart(2, '0'));
  }
}

async function main() {
  try {
    // Ensure output directory exists
    await fs.mkdir(options.output, { recursive: true });

    let weeksToExport = [];

    if (options.all) {
      weeksToExport = await getAvailableWeeks();
      console.log(`Exporting all available weeks: ${weeksToExport.join(', ')}`);
    } else if (options.week) {
      weeksToExport = [options.week.padStart(2, '0')];
      console.log(`Exporting week ${options.week}`);
    } else {
      console.error('Please specify either --week <week> or --all');
      process.exit(1);
    }

    console.log(`Output directory: ${options.output}`);
    console.log(`Server port: ${options.port}`);
    console.log(`Slide dimensions: ${options.width}x${options.height}`);
    console.log('');

    let successCount = 0;
    let totalCount = weeksToExport.length;

    for (const week of weeksToExport) {
      const success = await exportWeekToPDF(
        week,
        options.output,
        options.port,
        options.width,
        options.height
      );
      if (success) successCount++;
    }

    console.log('');
    console.log(`Export completed: ${successCount}/${totalCount} successful`);

    if (successCount < totalCount) {
      process.exit(1);
    }
  } catch (error) {
    console.error('Export failed:', error.message);
    process.exit(1);
  }
}

// Check if script is run directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main();
}