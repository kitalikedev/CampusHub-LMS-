// Bộ component dùng chung (04 §6). Trang chỉ ghép các component này, không tự viết lại.
export { Button, ButtonLink, buttonClass } from "@/components/ui/button";
export { Checkbox, Field, Input, Select, Textarea } from "@/components/ui/form";
export { Alert, Badge, EmptyState, ErrorState, Forbidden, Skeleton, SkeletonBlock } from "@/components/ui/feedback";
export type { Tone } from "@/components/ui/feedback";
export { Card, DefinitionList, PageHeader, Stat, Table, Tabs, Td, Th } from "@/components/ui/layout";
export { ConfirmDialog, Dialog } from "@/components/ui/dialog";
export { ToastProvider, useToast } from "@/components/ui/toast";
export { useErrorText } from "@/components/ui/useErrorText";
