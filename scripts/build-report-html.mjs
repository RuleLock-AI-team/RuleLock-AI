import fs from 'fs'

const md = fs.readFileSync('FINAL_PROJECT_REPORT.md', 'utf8')

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

let html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RuleLock AI - Final Project Report</title>
<style>
  @page { size: A4; margin: 2.5cm 2.5cm 2.5cm 2.5cm; }
  body { font-family: "Calibri", "Segoe UI", Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #1a1a1a; max-width: 860px; margin: 0 auto; padding: 40px 20px; }
  h1, h2, h3, h4 { font-family: "Calibri", "Segoe UI", Arial, sans-serif; color: #0f172a; margin-top: 1.4em; margin-bottom: 0.5em; }
  h1 { font-size: 20pt; border-bottom: 2px solid #0284c7; padding-bottom: 6px; }
  h2 { font-size: 15pt; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-top: 1.8em; }
  h3 { font-size: 12.5pt; color: #0369a1; }
  h4 { font-size: 11pt; font-style: italic; }
  p { margin-bottom: 0.8em; text-align: justify; }
  table { width: 100%; border-collapse: collapse; margin: 1.4em 0; font-size: 9.5pt; page-break-inside: avoid; }
  th, td { border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; vertical-align: top; }
  th { background-color: #f1f5f9; font-weight: 600; color: #0f172a; }
  tr:nth-child(even) { background-color: #f8fafc; }
  pre, code { font-family: "Consolas", "Courier New", monospace; }
  pre { background-color: #0f172a; color: #f8fafc; padding: 14px; border-radius: 6px; overflow-x: auto; font-size: 9pt; line-height: 1.4; page-break-inside: avoid; margin: 1em 0; }
  p code, li code, td code { background-color: #f1f5f9; color: #b91c1c; padding: 2px 5px; border-radius: 4px; font-size: 9.5pt; }
  ul, ol { margin-bottom: 1em; padding-left: 1.5em; }
  li { margin-bottom: 0.3em; }
  blockquote { border-left: 4px solid #0284c7; padding-left: 15px; margin: 1em 0; color: #475569; font-style: italic; }
  hr { border: none; border-top: 1px solid #e2e8f0; margin: 2em 0; }
  .cover { text-align: center; padding: 40px 20px; border: 2px solid #cbd5e1; border-radius: 8px; margin-bottom: 40px; background: #fafafa; }
  .cover h1 { border: none; font-size: 22pt; color: #0369a1; margin-bottom: 8px; }
  .cover h2 { border: none; font-size: 13pt; color: #475569; font-weight: normal; margin-top: 0; }
</style>
</head>
<body>
`

const lines = md.split('\n')
let inPre = false
let preContent = ''
let inTable = false
let tableHtml = ''

for (let i = 0; i < lines.length; i++) {
  let line = lines[i]

  if (line.startsWith('```')) {
    if (inPre) {
      html += '<pre><code>' + escapeHtml(preContent) + '</code></pre>\n'
      preContent = ''
      inPre = false
    } else {
      inPre = true
    }
    continue
  }
  if (inPre) {
    preContent += line + '\n'
    continue
  }

  if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
    if (!inTable) {
      inTable = true
      tableHtml = '<table>\n'
      const cells = line.split('|').slice(1, -1).map(c => c.trim())
      tableHtml += '<thead><tr>' + cells.map(c => '<th>' + c + '</th>').join('') + '</tr></thead>\n<tbody>\n'
    } else if (line.includes('---')) {
      // separator
    } else {
      const cells = line.split('|').slice(1, -1).map(c => c.trim())
      tableHtml += '<tr>' + cells.map(c => '<td>' + c + '</td>').join('') + '</tr>\n'
    }
    continue
  } else if (inTable) {
    inTable = false
    tableHtml += '</tbody></table>\n'
    html += tableHtml
    tableHtml = ''
  }

  if (line.startsWith('# ')) {
    html += '<h1>' + line.slice(2) + '</h1>\n'
  } else if (line.startsWith('## ')) {
    html += '<h2>' + line.slice(3) + '</h2>\n'
  } else if (line.startsWith('### ')) {
    html += '<h3>' + line.slice(4) + '</h3>\n'
  } else if (line.startsWith('#### ')) {
    html += '<h4>' + line.slice(5) + '</h4>\n'
  } else if (line.trim() === '---') {
    html += '<hr>\n'
  } else if (line.startsWith('- ')) {
    html += '<li>' + line.slice(2) + '</li>\n'
  } else if (/^\d+\.\s/.test(line)) {
    html += '<li>' + line.replace(/^\d+\.\s/, '') + '</li>\n'
  } else if (line.trim().length > 0) {
    html += '<p>' + line + '</p>\n'
  }
}

if (inTable) {
  html += tableHtml + '</tbody></table>\n'
}

html += '</body>\n</html>'

html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')
html = html.replace(/`([^`]+)`/g, '<code>$1</code>')

fs.writeFileSync('FINAL_PROJECT_REPORT.html', html, 'utf8')
console.log('FINAL_PROJECT_REPORT.html successfully built!')
