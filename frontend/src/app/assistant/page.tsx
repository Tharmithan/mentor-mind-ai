import { PageHeader } from "@/components/ui/PageHeader";
import { ChatAssistant } from "@/components/assistant/ChatAssistant";

export default function AssistantPage() {
  return (
    <>
      <PageHeader
        title="AI Study Assistant"
        subtitle="Upload your notes and chat with an AI tutor that answers from your own material"
      />
      <ChatAssistant />
    </>
  );
}
