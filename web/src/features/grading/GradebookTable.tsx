"use client";
// Sổ điểm của lớp: SV × bài, điểm tạm tính, kết quả khi đã khóa sổ (FR-GRD-03).
import { useState } from "react";

import { Button, EmptyState, ErrorState, SkeletonBlock, Table, Td, Th, useErrorText, useToast } from "@/components/ui";
import { api, saveBlob } from "@/lib/api/client";
import { useApi } from "@/lib/api/useApi";
import { formatNumber } from "@/lib/format";
import { useI18n } from "@/lib/i18n/I18nProvider";
import type { Gradebook } from "@/types/api";

export function GradebookTable({ sectionId }: { sectionId: number }) {
  const { t, locale } = useI18n();
  const book = useApi<Gradebook>(`/sections/${sectionId}/gradebook`);
  const toast = useToast();
  const errorText = useErrorText();
  const [exporting, setExporting] = useState(false);

  // Tải CSV cần token nên đi qua axios rồi lưu blob (BR-GRD-07).
  async function exportCsv() {
    setExporting(true);
    try {
      const res = await api.get<Blob>(`/sections/${sectionId}/gradebook.csv`, { responseType: "blob" });
      const match = /filename="([^"]+)"/.exec(String(res.headers["content-disposition"] ?? ""));
      saveBlob(res.data, match ? match[1] : `gradebook_${sectionId}.csv`);
    } catch (err) {
      toast(errorText(err), "danger");
    } finally {
      setExporting(false);
    }
  }

  if (book.error) return <ErrorState error={book.error} onRetry={book.reload} />;
  if (!book.data) return <SkeletonBlock />;
  const { assignments, rows, weight_total: total } = book.data;
  if (!rows.length) return <EmptyState title={t("gradebook.noStudents")} />;
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-muted">{t("gradebook.hint", { total: formatNumber(total, locale, 0) })}</p>
        <Button variant="secondary" size="sm" loading={exporting} onClick={exportCsv}>{t("gradebook.exportCsv")}</Button>
      </div>
      <Table>
        <thead>
          <tr>
            <Th>{t("gradebook.student")}</Th>
            {assignments.map((a) => (
              <Th key={a.id} className="text-right">{a.title}<br /><span className="font-normal">{formatNumber(a.weight_percent, locale, 0)}%</span></Th>
            ))}
            <Th className="text-right">{t("gradebook.provisional")}</Th>
            <Th className="text-right">{t("gradebook.final")}</Th>
          </tr>
        </thead>
        <tbody className="divide-y divide-line">
          {rows.map((row) => (
            <tr key={row.student.id}>
              <Td>
                <p className="font-medium">{row.student.full_name}</p>
                <p className="text-xs text-muted">{row.student.student_code} · {row.student.email}</p>
              </Td>
              {assignments.map((a) => (
                <Td key={a.id} className="text-right tabular-nums">{formatNumber(row.scores[String(a.id)], locale)}</Td>
              ))}
              <Td className="text-right tabular-nums">
                {formatNumber(row.provisional_score, locale)}
                <span className="block text-xs text-muted">{t("gradebook.weightGraded", { w: formatNumber(row.graded_weight, locale, 0) })}</span>
              </Td>
              <Td className="text-right tabular-nums">
                {row.result ? `${formatNumber(row.result.final_score_10, locale)} · ${row.result.letter_grade ?? (row.result.is_passed ? t("transcript.pass") : t("transcript.fail"))}` : "—"}
              </Td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}
