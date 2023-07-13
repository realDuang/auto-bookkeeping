import { RecordType, type IBookKeepingRow, type KeywordsMap } from "../types";
import Settings from "../../config/settings.json";

export async function billPreprocessor(
  bookKeepRecords: IBookKeepingRow[]
): Promise<IBookKeepingRow[]> {
  // 优先去掉非收支部分
  const filteredBookKeepRecords = bookKeepRecords.filter((row) => {
    return !(row["收/支"] === "/" && !row["商品名称"].includes("退款"));
  });

  const keywordsMap = Settings.keywords as unknown as KeywordsMap;
  const keywords = Object.keys(keywordsMap);
  const recordTypes = Object.values(RecordType);

  const autoFillBookKeepRecords = filteredBookKeepRecords.map((row) => {
    if (row["类型"] !== "") return row;

    const keyword = keywords.find((keyword) =>
      row["商品名称"].includes(keyword)
    );
    if (keyword && recordTypes.some((type) => type === keywordsMap[keyword])) {
      row["类型"] = keywordsMap[keyword] as RecordType;
      return row;
    }

    return row;
  });

  return autoFillBookKeepRecords;
}
