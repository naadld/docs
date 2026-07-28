export interface Env {
  TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_SECRET_TOKEN?: string;
  ALLOWED_CHAT_IDS: string; // Comma-separated user/chat/group IDs allowed
  TARGET_VPS_ID: string; // "vpsg24gb", "vpsg16gb", or "hariinc"
  CLOUDFLARE_API_TOKEN?: string;
  CLOUDFLARE_ACCOUNT_ID?: string;
  SERVICE_ACCOUNT_PRIVATE_KEY?: string;
  GH_PAT?: string;
  GH_REPO_OWNER?: string;
  GH_REPO_NAME?: string;
  VPS_NODES?: string; // JSON string representing VPS Node configs
  VPS_KV?: KVNamespace;
}

export interface VPSNode {
  id: string;
  name: string;
  url: string; // Cloudflare Tunnel domain or HTTPS URL (e.g. https://vps1.mydomain.com)
  token: string; // Authentication bearer token
}

export interface TelegramUser {
  id: number;
  is_bot: boolean;
  first_name: string;
  last_name?: string;
  username?: string;
}

export interface TelegramChat {
  id: number;
  type: string;
  title?: string;
  username?: string;
}

export interface TelegramMessage {
  message_id: number;
  from?: TelegramUser;
  chat: TelegramChat;
  date: number;
  text?: string;
  caption?: string;
  message_thread_id?: number; // Forum Topic ID in Telegram Supergroups
  reply_to_message?: TelegramMessage;
  document?: {
    file_id: string;
    file_unique_id: string;
    file_name?: string;
    mime_type?: string;
    file_size?: number;
  };
}

export interface TelegramCallbackQuery {
  id: string;
  from: TelegramUser;
  message?: TelegramMessage;
  data?: string;
}

export interface TelegramUpdate {
  update_id: number;
  message?: TelegramMessage;
  callback_query?: TelegramCallbackQuery;
}

export interface CommandResponse {
  success: boolean;
  message: string;
  data?: any;
}
