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
 * Trigger GitHub Actions Media Downloader Engine via repository_dispatch API with 5 Colab Profiles Rotation
 */
export async function handleMediaAction(
  env: Env,
  chatId: number | string,
  threadId: number | undefined,
  mediaUrl: string,
  action: string = 'video'
) {
  let actionTitle = 'DOWNLOAD MEDIA VIDEO';
  if (action.includes('mp3')) actionTitle = 'DOWNLOAD AUDIO MP3';
  if (action.includes('pl')) actionTitle = 'DOWNLOAD PLAYLIST';

  const profileIndex = getNextColabProfileIndex();

  await sendTelegramMessage(
    env,
    chatId,
    `🚀 <b>HaRi Colab CLI [Profile #${profileIndex}]:</b> Triggering <b>[${actionTitle}]</b> for <code>${escapeHtml(mediaUrl.substring(0, 80))}</code>...`,
    'HTML',
    undefined,
    threadId
  );

  const ghToken = env.GH_PAT || "";
  const repoOwner = env.GH_REPO_OWNER || "naadld";
  const repoName = env.GH_REPO_NAME || "docs";

  const url = `https://api.github.com/repos/${repoOwner}/${repoName}/dispatches`;
  const payload = {
    event_type: "download-media",
    client_payload: {
      chat_id: chatId,
      thread_id: threadId || 6,
      url: mediaUrl,
      action: action,
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
        `⚡ <b>Colab Engine Dispatched!</b> Downloading media via Gmail Profile #${profileIndex}, uploading to Google Drive Folder <code>1itDlaeJyzmp6m91RDtU6WzwhpL3Hq9pD</code>...`,
        'HTML',
        undefined,
        threadId
      );
    } else {
      const errText = await res.text();
      await sendTelegramMessage(
        env,
        chatId,
        `❌ <b>GitHub Media Dispatch Error (${res.status}):</b> ${escapeHtml(errText)}`,
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
