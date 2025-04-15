import { IBookKeepingRow } from "../types";
import { formatBillRecords } from "./formatter";

export const processTransactions = async (files: FileList) => {
  const allTransactions: IBookKeepingRow[] = [];

  for (let i = 0; i < files.length; i++) {
    try {
      const transactions = await formatBillRecords(files[i]);
      allTransactions.push(...transactions);
    } catch (err) {
      console.error("处理文件时出错:", err);
    }
  }

  allTransactions.sort((a, b) => {
    return a.交易时间.getTime() - b.交易时间.getTime();
  });

  return allTransactions;
};

export const handleFileExport = async (
  transactions: IBookKeepingRow[] | null
) => {
  const csvContent = transactions
    ? transactions.map((row) => Object.values(row).join(",")).join("\n")
    : "";

  const blob = new Blob([csvContent], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "processed_transactions.csv";
  a.click();
  window.URL.revokeObjectURL(url);
};
