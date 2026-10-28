import { env } from 'cloudflare:workers';
import { getChatGPTUser } from '../../chatgpt-auth';
import { validState } from '../../../lib/validate';
const json = (body: unknown, status=200)=>Response.json(body,{status,headers:{'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff'}});
export async function GET() {
  const user=await getChatGPTUser();if(!user)return json({error:'Sign in to continue.'},401);
  const row=await env.DB.prepare('SELECT state, revision, updated_at FROM study_progress WHERE user_id = ?').bind(user.userId).first<{state:string;revision:number;updated_at:number}>();
  return json({userId:user.userId,revision:row?.revision||0,state:row?JSON.parse(row.state):null,updatedAt:row?.updated_at||null});
}
export async function PUT(request:Request) {
  const user=await getChatGPTUser();if(!user)return json({error:'Sign in to continue.'},401);
  if(request.headers.get('origin')!==new URL(request.url).origin)return json({error:'Origin not allowed.'},403);
  if(!request.headers.get('content-type')?.startsWith('application/json'))return json({error:'JSON required.'},415);
  const text=await request.text();if(text.length>250000)return json({error:'Backup too large.'},413);
  let body;try{body=JSON.parse(text)}catch{return json({error:'Invalid JSON.'},400)}
  if(!Number.isSafeInteger(body.revision)||body.revision<0||!validState(body.state))return json({error:'Invalid study progress.'},400);
  const content=JSON.stringify(body.state),now=Date.now();
  const result=body.revision===0
    ?await env.DB.prepare('INSERT INTO study_progress (user_id,state,revision,updated_at) VALUES (?,?,1,?) ON CONFLICT(user_id) DO NOTHING').bind(user.userId,content,now).run()
    :await env.DB.prepare('UPDATE study_progress SET state = ?, revision = revision + 1, updated_at = ? WHERE user_id = ? AND revision = ?').bind(content,now,user.userId,body.revision).run();
  if(result.meta.changes!==1)return json({error:'Another device saved newer progress. Choose which version to keep.'},409);
  return json({revision:body.revision+1,updatedAt:now});
}
