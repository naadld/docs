import { Env, VPSNode, CommandResponse } from './types';

/**
 * Lấy danh sách VPS từ biến môi trường hoặc KV Store
 */
export async function getVPSList(env: Env): Promise<VPSNode[]> {
  // Thử đọc từ KV nếu có
  if (env.VPS_KV) {
    try {
      const kvData = await env.VPS_KV.get('VPS_NODES');
      if (kvData) {
        return JSON.parse(kvData);
      }
    } catch (e) {
      console.error('Error reading VPS from KV:', e);
    }
  }

  // Đọc từ biến môi trường VPS_NODES
  if (env.VPS_NODES) {
    try {
      return JSON.parse(env.VPS_NODES);
    } catch (e) {
      console.error('Error parsing VPS_NODES env:', e);
    }
  }

  // Mẫu mặc định nếu chưa cấu hình
  return [];
}

/**
 * Lấy VPS Node theo ID hoặc Name
 */
export async function findVPS(env: Env, query: string): Promise<VPSNode | undefined> {
  const nodes = await getVPSList(env);
  const q = query.trim().toLowerCase();
  return nodes.find(n => n.id.toLowerCase() === q || n.name.toLowerCase() === q);
}

/**
 * Lấy trạng thái tài nguyên (CPU, RAM, Disk, Uptime) của 1 VPS
 */
export async function fetchVPSStatus(node: VPSNode): Promise<CommandResponse> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 seconds timeout

    const res = await fetch(`${node.url}/status`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${node.token}`,
        'User-Agent': 'iHoangTelegram-Worker/1.0',
      },
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      return {
        success: false,
        message: `HTTP ${res.status}: ${res.statusText}`,
      };
    }

    const data = await res.json();
    return {
      success: true,
      message: 'OK',
      data: data,
    };
  } catch (err: any) {
    return {
      success: false,
      message: err.name === 'AbortError' ? 'Timeout (Không phản hồi sau 8s)' : (err.message || 'Lỗi kết nối tới VPS'),
    };
  }
}

/**
 * Gửi lệnh điều khiển thực thi trên VPS
 */
export async function execVPSCommand(node: VPSNode, command: string): Promise<CommandResponse> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 seconds timeout

    const res = await fetch(`${node.url}/exec`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${node.token}`,
        'User-Agent': 'iHoangTelegram-Worker/1.0',
      },
      body: JSON.stringify({ command }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    const data: any = await res.json();
    if (!res.ok || !data.success) {
      return {
        success: false,
        message: data.error || data.message || `Lỗi HTTP ${res.status}`,
        data: data,
      };
    }

    return {
      success: true,
      message: data.output || 'Thực thi thành công (Không có output)',
      data: data,
    };
  } catch (err: any) {
    return {
      success: false,
      message: err.name === 'AbortError' ? 'Timeout (Lỗi thực thi quá 15s)' : (err.message || 'Lỗi kết nối tới VPS'),
    };
  }
}

/**
 * Gửi yêu cầu khởi động lại VPS
 */
export async function rebootVPS(node: VPSNode): Promise<CommandResponse> {
  try {
    const res = await fetch(`${node.url}/reboot`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${node.token}`,
        'User-Agent': 'iHoangTelegram-Worker/1.0',
      },
    });

    const data: any = await res.json();
    return {
      success: res.ok && data.success,
      message: data.message || (res.ok ? 'Lệnh khởi động lại đã được gửi' : 'Khởi động lại thất bại'),
    };
  } catch (err: any) {
    return {
      success: false,
      message: err.message || 'Lỗi kết nối tới VPS',
    };
  }
}
