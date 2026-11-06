import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath,pathToFileURL} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const require=createRequire(import.meta.url);
const {chromium}=require('playwright');
for(const dir of ['pdf','preview','qa'])await fs.mkdir(path.join(here,'..',dir),{recursive:true});
const browser=await chromium.launch({...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{}),headless:true});
const page=await browser.newPage({viewport:{width:624,height:800},deviceScaleFactor:2});
const specs=JSON.parse(await fs.readFile(path.join(here,'manifest.json'),'utf8'));
const report=[];
for(const s of specs){
 await page.goto(pathToFileURL(path.join(here,s.stem+'.html')).href);
 await page.evaluate(()=>document.fonts.ready);
 // Place underlines below the actual glyph bounds, not through the brackets.
 await page.locator('svg').evaluate(svg=>{
  svg.querySelectorAll('[data-window-row]').forEach(row=>{
   const items=[...row.querySelectorAll('[data-window-item]')],gap=Number(row.dataset.gap);
   const bounds=items.map(item=>item.getBBox());
   let x=Number(row.dataset.center)-(bounds.reduce((s,b)=>s+b.width,0)+gap*(items.length-1))/2;
   items.forEach((item,i)=>{
    const dx=x-bounds[i].x;
    item.querySelectorAll('text').forEach(t=>t.setAttribute('x',Number(t.getAttribute('x'))+dx));
    x+=bounds[i].width+gap;
   });
  });
  svg.querySelectorAll('[data-underline]').forEach(x=>x.remove());
  svg.querySelectorAll('tspan[data-waning="1"]').forEach(span=>{
   const b=span.getBBox(),parent=span.parentElement,y=Number(parent.getAttribute('y'))+6;
   const line=document.createElementNS('http://www.w3.org/2000/svg','line');
   for(const [k,v] of Object.entries({'x1':b.x,'x2':b.x+b.width,'y1':y,'y2':y,'stroke':getComputedStyle(parent).fill,'stroke-width':1.1,'data-underline':'true'}))line.setAttribute(k,v);
   svg.appendChild(line);
  });
 });
 const metrics=await page.locator('svg').evaluate(svg=>({
  text:[...svg.querySelectorAll('text')].map(t=>{const b=t.getBBox();return{text:t.textContent,x:b.x,y:b.y,w:b.width,h:b.height,fontSizePt:Number(getComputedStyle(t).fontSize.replace('px',''))*.75};}),
  boxes:Object.fromEntries([...svg.querySelectorAll('[data-box]')].map(b=>[b.dataset.box,{x:b.x.baseVal.value,y:b.y.baseVal.value,w:b.width.baseVal.value,h:b.height.baseVal.value}])),
  cells:[...svg.querySelectorAll('[data-cell]')].map(c=>({w:c.width.baseVal.value,h:c.height.baseVal.value})),
 }));
 const smallText=metrics.text.filter(t=>t.fontSizePt<10.5);
 const clipped=metrics.text.filter(t=>t.x<0||t.y<0||t.x+t.w>624||t.y+t.h>s.height);
 const overlap=[];
 for(let i=0;i<metrics.text.length;i++)for(let j=i+1;j<metrics.text.length;j++){
  const a=metrics.text[i],b=metrics.text[j];
  if(Math.min(a.x+a.w,b.x+b.w)-Math.max(a.x,b.x)>1&&Math.min(a.y+a.h,b.y+b.h)-Math.max(a.y,b.y)>2)overlap.push([a.text,b.text]);
 }
 function onBorder(p,b){return p[0]>=b.x-.1&&p[0]<=b.x+b.w+.1&&p[1]>=b.y-.1&&p[1]<=b.y+b.h+.1&&Math.min(Math.abs(p[0]-b.x),Math.abs(p[0]-b.x-b.w),Math.abs(p[1]-b.y),Math.abs(p[1]-b.y-b.h))<.1;}
 const arrows=s.edges.map(e=>({...e,attached:onBorder(e.start,metrics.boxes[e.from])&&onBorder(e.end,metrics.boxes[e.to])}));
 const aligned=s.groups.every(ids=>{const a=metrics.boxes[ids[0]];return ids.every(id=>{const b=metrics.boxes[id];return ['y','w','h'].every(k=>Math.abs(a[k]-b[k])*.75<=1.5);});});
 const equalCells=metrics.cells.length===0||metrics.cells.every(c=>c.w===metrics.cells[0].w&&c.h===metrics.cells[0].h);
 const result={figure:s.stem,smallText,clipped,textOverlap:overlap,arrows,alignment:{status:aligned?'PASS':'FAIL',tolerancePt:1.5,groups:s.groups,boxes:metrics.boxes},equalCells:{status:equalCells?'PASS':'FAIL',count:metrics.cells.length,sizeCssPx:metrics.cells[0]},text:metrics.text};
 report.push(result);
 if(smallText.length||clipped.length||overlap.length||arrows.some(a=>!a.attached)||!aligned||!equalCells){console.log(JSON.stringify(result));throw new Error('Rendered layout audit failed');}
 const svg=await page.locator('svg').evaluate(e=>e.outerHTML);
 await fs.writeFile(path.join(here,s.stem+'.svg'),svg);
 await fs.writeFile(path.join(here,s.stem+'.html'),await page.content());
 await page.pdf({path:path.join(here,'../pdf',s.stem+'.pdf'),printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false});
 await page.locator('svg').screenshot({path:path.join(here,'../preview',s.stem+'.png')});
 console.log('Exported '+s.stem+'; all arrows attach to boxes.');
}
await fs.writeFile(path.join(here,'../qa/layout.json'),JSON.stringify(report,null,2));
await fs.writeFile(path.join(here,'../qa/collisions.json'),JSON.stringify(report.map(r=>({figure:r.figure,status:'PASS',textText:r.textOverlap,pageClipping:r.clipped,arrowAttachments:r.arrows.map(a=>a.attached),note:'Cell backgrounds and intentional cell outlines are exempt; text/line crossings also reviewed in rendered PDF.'})),null,2));
await browser.close();
