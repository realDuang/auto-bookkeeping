import { wechatPayFormatter } from "./wechatPayFormatter";
import { aliPayFormatter } from "./alipayFormatter";
import type { IBookKeepingRow } from "../types";

export async function formatBillRecords(filePaths: {
  aliPayOriginPath?: string;
  wechatPayOriginPath?: string;
}): Promise<IBookKeepingRow[]> {
  const { aliPayOriginPath, wechatPayOriginPath } = filePaths;

  let aliPayRecords: IBookKeepingRow[] = [];
  if (aliPayOriginPath) {
    aliPayRecords = await aliPayFormatter(aliPayOriginPath);
  }
  let wechatPayRecords: IBookKeepingRow[] = [];
  if (wechatPayOriginPath) {
    wechatPayRecords = await wechatPayFormatter(wechatPayOriginPath);
  }

  const bookKeepRecords = [...aliPayRecords, ...wechatPayRecords].sort(
    (a, b) => {
      return a.交易时间.getTime() - b.交易时间.getTime();
    }
  );
  return bookKeepRecords;
}
