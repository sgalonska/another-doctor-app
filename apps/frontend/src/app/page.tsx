import { Suspense } from 'react';
import { DiagnosisAssistant } from "@/components/assistant/diagnosis-assistant";

function AssistantWrapper() {
  return <DiagnosisAssistant />;
}

export default function Home() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-bg-light flex items-center justify-center">Loading...</div>}>
      <AssistantWrapper />
    </Suspense>
  );
}