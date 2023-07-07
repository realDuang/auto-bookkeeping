import { formatBillToCsv } from "./formatter";
import path from "path";

const aliPayOriginPath = path.resolve(
  __dirname,
  "../../data-source/origin-data/alipay_record.csv"
);
const wechatPayOriginPath = path.resolve(
  __dirname,
  "../../data-source/origin-data/wechat_record.csv"
);
const destinationPath = path.resolve(
  __dirname,
  "../../data-source/formatted-data.csv"
);

formatBillToCsv({
  aliPayOriginPath,
  wechatPayOriginPath,
  destinationPath,
});
