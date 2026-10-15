// Execute in functions.exec (connector orchestration), not in a shell or browser.
// Only traverses the two explicitly configured vaults. Never follows shortcuts.
const roots=[
 {id:'public-library',name:'Public Library',url:'https://drive.google.com/drive/folders/0B9wuggJUWO5PejkzOUJZTWx6NGM?resourcekey=0-CHaAwLapPnvIJ7BW3Nj8jw'},
 {id:'bookshelf',name:'My Bookshelf',url:'https://drive.google.com/drive/folders/1NvUlp3CWKggnwhxBS862_2i1LsIEOsxM'}
];
const result={started_at:new Date().toISOString(),complete:false,vaults:{},errors:[]};
for(const root of roots){
 const state={name:root.name,files:[],folders:[],shortcuts:[]};result.vaults[root.id]=state;
 const queue=[{url:root.url,path:''}],seen=new Set();let completed=0;
 while(queue.length){
  const batch=queue.splice(0,6);
  const responses=await Promise.allSettled(batch.map(async folder=>{
   if(seen.has(folder.url))return;seen.add(folder.url);
   let response,data;
   for(let attempt=0;attempt<3;attempt++){
    try{response=await tools.mcp__codex_apps__google_drive_list_folder({url:folder.url,top_k:1000});data=response.structuredContent;if(Array.isArray(data?.files))break;}catch(error){if(attempt===2)throw error;}
   }
   if(response.isError||!Array.isArray(data?.files))throw Error(JSON.stringify(data||response).slice(0,300));
   if(data.files.length>=1000||data.next_page_token||data.nextPageToken)throw Error('Listing may be truncated: '+folder.path+'; pagination must be completed before checkpointing.');
   state.folders.push({url:folder.url,path:folder.path,count:data.files.length});
   for(const file of data.files){
    if(file.mime_type==='application/vnd.google-apps.shortcut'){state.shortcuts.push({id:file.id,title:file.title,folder:folder.path});continue;}
    if(file.mime_type==='application/vnd.google-apps.folder'){queue.push({url:file.url,path:folder.path?folder.path+'/'+file.title:file.title});continue;}
    state.files.push({id:file.id,title:file.title,mime_type:file.mime_type,size:file.size,url:file.url,folder:folder.path,modified_time:file.modified_time||file.updated_at||null,created_time:file.created_time||file.created_at||null});
   }
  }));
  for(let i=0;i<responses.length;i++)if(responses[i].status==='rejected')result.errors.push({vault:root.id,url:batch[i].url,folder:batch[i].path,error:String(responses[i].reason)});
  completed+=batch.length;if(completed%24<6)notify({vault:root.name,folders:completed,files:state.files.length});
 }
 state.files.sort((a,b)=>a.id.localeCompare(b.id));
}
result.complete=result.errors.length===0;result.finished_at=new Date().toISOString();
store('latestVaultScan',result);
const path='C:/Users/ehsan.bagherzadeh/Downloads/Bookshelf/my-public-library-catalog/latest_scan.local.json';
await tools.apply_patch('*** Begin Patch\n*** Add File: '+path+'\n+'+JSON.stringify(result).split('\n').join('\n+')+'\n*** End Patch');
text({complete:result.complete,errors:result.errors,counts:Object.fromEntries(Object.entries(result.vaults).map(([id,v])=>[id,{files:v.files.length,folders:v.folders.length,shortcuts:v.shortcuts.length}]))});
