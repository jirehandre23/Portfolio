import { getChatGPTUser, chatGPTSignInPath } from '../chatgpt-auth';
import { studyHtml } from '../../lib/study-html';
export async function GET(request: Request) {
  const user = await getChatGPTUser();
  if (!user) return Response.redirect(new URL(chatGPTSignInPath('/study'), request.url));
  return new Response(studyHtml, {headers: {'Content-Type':'text/html; charset=utf-8','Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'same-origin'}});
}
