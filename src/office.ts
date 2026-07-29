import { Env } from './types';
import { sendTelegramMessage } from './telegram';
import { getNextColabProfileIndex } from './colab_rotation';

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Trigger GitHub Actions Runner Engine via repository_dispatch API with 5 Colab Profiles Rotation
 */
export async function handleOfficeAction(
  env: Env,
  chatId: number | string,
  threadId: number | undefined,
  action: string,
  fileName: string = 'document.pdf',
  fileId?: string,
  messageId?: number
) {
  let actionTitle = 'CONVERT TO PDF';

  if (action === 'pdf') actionTitle = 'CONVERT TO PDF';
  else if (action === 'epub') actionTitle = 'CONVERT TO EPUB';
  else if (action === 'unlock') actionTitle = 'UNLOCK PDF PASSWORD';
  else if (action === 'docs') actionTitle = 'CONVERT PDF TO DOCS';
  else if (action === 'png') actionTitle = 'CONVERT TO PNG IMAGES';
  else if (action === 'split') actionTitle = 'SPLIT PDF PAGES';
  else if (action === 'excel') actionTitle = 'CONVERT TO EXCEL';
  else if (action === 'compress') actionTitle = 'COMPRESS PDF FILE SIZE';

  const profileIndex = getNextColabProfileIndex();

  await sendTelegramMessage(
    env,
    chatId,
    `🚀 <b>HaRi Colab CLI [Profile #${profileIndex}]:</b> Triggering <b>[${actionTitle}]</b> for <code>${escapeHtml(fileName)}</code>...`,
    'HTML',
    undefined,
    threadId
  );

  const ghToken = env.GH_PAT || "";
  const repoOwner = env.GH_REPO_OWNER || "naadld";
  const repoName = env.GH_REPO_NAME || "docs";

  const url = `https://api.github.com/repos/${repoOwner}/${repoName}/dispatches`;
  const payload = {
    event_type: "convert-document",
    client_payload: {
      action,
      chat_id: chatId,
      thread_id: threadId,
      file_id: fileId,
      file_name: fileName,
      message_id: messageId,
      profile_index: profileIndex,
    },
  };

  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${ghToken}`,
        "Accept": "application/vnd.github+json",
        "User-Agent": "CloudflareWorker-TelegramBot",
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (res.ok || res.status === 204) {
      await sendTelegramMessage(
        env,
        chatId,
        `⚡ <b>Colab Engine Dispatched!</b> Processing <code>${escapeHtml(fileName)}</code> via Gmail Profile #${profileIndex}. Output will arrive shortly!`,
        'HTML',
        undefined,
        threadId
      );
    } else {
      const errText = await res.text();
      await sendTelegramMessage(
        env,
        chatId,
        `❌ <b>GitHub Dispatch Error (${res.status}):</b> ${escapeHtml(errText)}`,
        'HTML',
        undefined,
        threadId
      );
    }
  } catch (err: any) {
    await sendTelegramMessage(
      env,
      chatId,
      `❌ <b>Dispatch Exception:</b> ${escapeHtml(err.message)}`,
      'HTML',
      undefined,
      threadId
    );
  }
}

export async function processOfficeDocument(
  env: Env,
  chatId: number | string,
  threadId: number | undefined,
  telegramFileUrl: string,
  originalFileName: string,
  targetFormat: string = 'pdf'
) {
  await handleOfficeAction(env, chatId, threadId, targetFormat, originalFileName);
}
