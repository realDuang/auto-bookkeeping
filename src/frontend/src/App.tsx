import { useState, useCallback } from "react";
import { FileUpload } from "./components/FileUpload";
import { handleFileExport, processTransactions } from "./utils/processData";
import { IBookKeepingRow } from "./types";
import { Download } from "lucide-react";
import { TransactionList } from "./components/TransactionList";

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [processedData, setProcessedData] = useState<IBookKeepingRow[] | null>(
    null
  );

  const handleFilesSelected = useCallback(async (files: FileList) => {
    setIsProcessing(true);
    try {
      const processed = await processTransactions(files);
      setProcessedData(processed);
    } catch (error) {
      console.error("Error processing files:", error);
      alert("处理文件时出错。当前仅支持 csv 格式文件。请检查格式后重试。");
    } finally {
      setIsProcessing(false);
    }
  }, []);

  const handleExport = useCallback(() => {
    handleFileExport(processedData);
  }, [processedData]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            智能账单整理工具
          </h1>

          <FileUpload
            onFilesSelected={handleFilesSelected}
            isProcessing={isProcessing}
          />
        </div>

        {processedData && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold text-gray-900">
                  支出分析
                </h2>
                <button
                  onClick={handleExport}
                  className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <Download className="w-4 h-4 mr-2" />
                  导出CSV
                </button>
              </div>
              {/* <TransactionChart data={processedData.categoryTotals} /> */}
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                交易记录
              </h2>
              <TransactionList transactions={processedData} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
