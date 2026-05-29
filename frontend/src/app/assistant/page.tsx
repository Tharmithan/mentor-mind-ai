import { PageHeader } from "@/components/ui/PageHeader";
import { AssistantWorkspace } from "@/components/assistant/AssistantWorkspace";

export default function AssistantPage() {
  return (
    <>
      <PageHeader
        title="AI Study Assistant"
        subtitle="Upload your notes, chat with an AI tutor, and generate summaries, quizzes, flashcards & revision sheets"
      />
      <AssistantWorkspace />
    </>
  );
}
