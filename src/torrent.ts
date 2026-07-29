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
 * Trigger GitHub Actions Torrent Downloader Engine via repository_dispatch API with 5 Colab Profiles Rotation
 */
export async function handleTorrentAction(
  env: Env,
  chatId: number | string,
  threadId: number | undefined,
  target: string,
  fileId?: string,
  messageId?: number
) {
  const profileIndex = getNextColabProfileIndex();

  await sendTelegramMessage(
    env,
    chatId,
    `🚀 <b>HaRI Colab CLI [Profile #${profileIndex}]:</b> Triggering <b>[TORRENT DOWNLOAD & GDRIVE UPLOAD]</b> for <code>${escapeHtml(target.substring(0, 80))}</code>...`,
    'HTML',
    undefined,
    threadId
  );

  const ghToken = env.GH_PAT || "";
  const repoOwner = env.GH_REPO_OWNER || "naadld";
  const repoName = env.GH_REPO_NAME || "docs";

  const url = `https://api.github.com/repos/${repoOwner}/${repoName}/dispatches`;
  const payload = {
    event_type: "download-torrent",
    client_payload: {
      chat_id: chatId,
      thread_id: threadId || 5,
      target,
      file_id: fileId,
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
        `⚡ <b>Colab Engine Dispatched!</b> Downloading Torrent via Gmail Profile #${profileIndex} & uploading to Google Drive Folder <code>1iuTERzYgM_tPiHcdc3CSxIsJdK96a5GO</code>...`,
        'HTML',
        undefined,
        threadId
      );
    } else {
      const errText = await res.text();
      await sendTelegramMessage(
        env,
        chatId,
        `❌ <b>GitHub Torrent Dispatch Error (${res.status}):</b> ${escapeHtml(errText)}`,
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
