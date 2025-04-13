import path from "path";
import { wechatPayFormatter } from "./wechatPayFormatter";
import { aliPayFormatter } from "./alibabaPayFormatter";
import type { IBookKeepingRow } from "../types";
import {
  aliPayOriginPath,
  wechatPayOriginPath,
} from "../../../config/settings.json";

export async function formatBillRecords(): Promise<IBookKeepingRow[]> {
  let aliPayRecords: IBookKeepingRow[] = [];
  if (aliPayOriginPath) {
    aliPayRecords = await aliPayFormatter(
      path.resolve(process.cwd(), aliPayOriginPath)
    );
  }

  let wechatPayRecords: IBookKeepingRow[] = [];
  if (wechatPayOriginPath) {
    wechatPayRecords = await wechatPayFormatter(
      path.resolve(process.cwd(), wechatPayOriginPath)
    );
  }

  const bookKeepRecords = [...aliPayRecords, ...wechatPayRecords].sort(
    (a, b) => {
      return a.交易时间.getTime() - b.交易时间.getTime();
    }
  );
  return bookKeepRecords;
}
