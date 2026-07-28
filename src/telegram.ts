import { Env } from './types';

/**
 * Send Telegram message supporting Forum Topics (message_thread_id) & Reply to Message ID
 */
export async function sendTelegramMessage(
  env: Env,
  chatId: number | string,
  text: string,
  parseMode: 'HTML' | 'MarkdownV2' = 'HTML',
  replyMarkup?: any,
  messageThreadId?: number,
  replyToMessageId?: number
): Promise<boolean> {
  const token = env.TELEGRAM_BOT_TOKEN;
  if (!token) {
    console.error('TELEGRAM_BOT_TOKEN is missing');
    return false;
  }

  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  
  const payload: any = {
    chat_id: chatId,
    text: text,
    parse_mode: parseMode,
    reply_markup: replyMarkup,
    disable_web_page_preview: true,
  };

  if (messageThreadId) {
    payload.message_thread_id = messageThreadId;
  }
  if (replyToMessageId) {
    payload.reply_to_message_id = replyToMessageId;
  }

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data: any = await res.json();
    if (!data.ok) {
      console.error('Telegram API error:', data);
      return false;
    }
    return true;
  } catch (err) {
    console.error('Failed to send Telegram message:', err);
    return false;
  }
}

/**
 * Send document file directly to Telegram chat/topic
 */
export async function sendTelegramDocument(
  env: Env,
  chatId: number | string,
  fileName: string,
  fileBuffer: ArrayBuffer,
  caption?: string,
  messageThreadId?: number
): Promise<boolean> {
  const token = env.TELEGRAM_BOT_TOKEN;
  if (!token) return false;

  const url = `https://api.telegram.org/bot${token}/sendDocument`;
  const formData = new FormData();
  formData.append('chat_id', chatId.toString());

  if (messageThreadId) {
    formData.append('message_thread_id', messageThreadId.toString());
  }
  if (caption) {
    formData.append('caption', caption);
    formData.append('parse_mode', 'HTML');
  }

  const blob = new Blob([fileBuffer]);
  formData.append('document', blob, fileName);

  try {
    const res = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    const data: any = await res.json();
    return data.ok;
  } catch (err) {
    console.error('Failed to send Telegram document:', err);
    return false;
  }
}

/**
 * Download binary file content directly from Telegram API using file_id
 */
export async function getTelegramFileBuffer(env: Env, fileId: string): Promise<ArrayBuffer> {
  const token = env.TELEGRAM_BOT_TOKEN;
  if (!token) throw new Error('TELEGRAM_BOT_TOKEN missing');

  const getFileRes = await fetch(`https://api.telegram.org/bot${token}/getFile?file_id=${fileId}`);
  const getFileData: any = await getFileRes.json();

  if (!getFileData.ok || !getFileData.result || !getFileData.result.file_path) {
    throw new Error(`Failed to locate file path on Telegram server: ${JSON.stringify(getFileData)}`);
  }

  const filePath = getFileData.result.file_path;
  const fileRes = await fetch(`https://api.telegram.org/file/bot${token}/${filePath}`);

  if (!fileRes.ok) {
    throw new Error(`Failed to download binary file content: ${fileRes.statusText}`);
  }

  return await fileRes.arrayBuffer();
}

/**
 * Answer callback query for inline keyboard buttons
 */
export async function answerCallbackQuery(
  env: Env,
  callbackQueryId: string,
  text?: string
): Promise<boolean> {
  const token = env.TELEGRAM_BOT_TOKEN;
  if (!token) return false;

  const url = `https://api.telegram.org/bot${token}/answerCallbackQuery`;
  try {
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        callback_query_id: callbackQueryId,
        text: text,
      }),
    });
    return true;
  } catch {
    return false;
  }
}

/**
 * Register bot commands with Telegram UI autocomplete menu
 */
export async function setMyCommands(env: Env): Promise<any> {
  const token = env.TELEGRAM_BOT_TOKEN;
  const role = env.TARGET_VPS_ID || 'hariinc';

  let commands: { command: string; description: string }[] = [];

  if (role === 'vpsg24gb') {
    commands = [
      { command: 'help', description: 'Show vpsg24gb instructions' },
      { command: 'status', description: 'View RAM/CPU/Disk metrics' },
      { command: 'optimize', description: 'Run system optimization analyzer' },
      { command: 'docker', description: 'View active docker containers' },
      { command: 'reboot', description: 'Reboot vpsg24gb server' },
    ];
  } else if (role === 'vpsg16gb') {
    commands = [
      { command: 'help', description: 'Show vpsg16gb instructions' },
      { command: 'status', description: 'View RAM/CPU/Disk metrics' },
      { command: 'optimize', description: 'Run system optimization analyzer' },
      { command: 'docker', description: 'View active docker containers' },
      { command: 'reboot', description: 'Reboot vpsg16gb server' },
    ];
  } else {
    commands = [
      { command: 'help', description: 'Show system guide & topics' },
      { command: 'cf', description: 'Check Cloudflare Workers quotas' },
      { command: 'convert', description: 'Convert document to PDF/EPUB' },
      { command: 'unlock', description: 'Unlock PDF password' },
      { command: 'torrent', description: 'Download magnet link to Google Drive' },
      { command: 'yt', description: 'Download YouTube video/audio' },
      { command: 'tiktok', description: 'Download TikTok video (No Watermark)' },
      { command: 'fb', description: 'Download Facebook Reels/Videos' },
      { command: 'mp3', description: 'Extract MP3 audio' },
    ];
  }

  const url = `https://api.telegram.org/bot${token}/setMyCommands`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ commands }),
  });

  return await res.json();
}

/**
 * Register Webhook with Telegram Server
 */
export async function registerWebhook(env: Env, workerUrl: string): Promise<any> {
  const token = env.TELEGRAM_BOT_TOKEN;
  const secret = env.TELEGRAM_SECRET_TOKEN;
  const webhookUrl = `${workerUrl}/webhook`;

  const url = `https://api.telegram.org/bot${token}/setWebhook`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url: webhookUrl,
      secret_token: secret,
      allowed_updates: ['message', 'callback_query'],
    }),
  });

  await setMyCommands(env);

  return await res.json();
}
