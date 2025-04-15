import { wechatPayFormatter } from "./wechatPayFormatter";
import { aliPayFormatter } from "./alibabaPayFormatter";
import type { IBookKeepingRow } from "../../types";

export async function formatBillRecords(
  file: File
): Promise<IBookKeepingRow[]> {
  const { name, type, size } = file;

  if (type != "text/csv") {
    alert("请上传csv格式的文件");
    return [];
  }

  if (size > 10 * 1024 * 1024) {
    alert("文件大小超过10MB，请上传小于10MB的文件");
    return [];
  }

  const billType = name.includes("alipay")
    ? "alipay"
    : name.includes("微信支付")
    ? "wechatpay"
    : "other";

  let payRecords: IBookKeepingRow[] = [];

  try {
    if (billType === "alipay") {
      payRecords = await aliPayFormatter(file);
    } else if (billType === "wechatpay") {
      payRecords = await wechatPayFormatter(file);
    } else {
      alert("请上传支付宝或微信支付的账单文件");
    }
  } catch (error) {
    console.error("格式化账单记录时出错:", error);
    throw new Error(`账单格式化失败: ${error instanceof Error ? error.message : String(error)}`);
  }

  return payRecords;
}

// 确保CSV转换函数正确工作
export async function transformCSVFileToBuffer(file: File): Promise<Buffer> {
  return new Promise<Buffer>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(Buffer.from(reader.result as ArrayBuffer));
    reader.onerror = (error) => reject(error);
    reader.readAsArrayBuffer(file);
  });
}

// 添加一个简单的CSV解析函数，避免依赖fast-csv
export async function parseCSV(file: File): Promise<string[][]> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split(/\r?\n/);
      const result = lines.map(line => line.split(','));
      resolve(result);
    };
    reader.onerror = reject;
    reader.readAsText(file);
  });
}
