import { PageHeader } from "@/components/ui/PageHeader";
import { ResumeAnalyzer } from "@/components/resume/ResumeAnalyzer";

export default function ResumePage() {
  return (
    <>
      <PageHeader
        title="Resume Analyzer"
        subtitle="Upload your PDF — AI checks missing skills, ATS compatibility, formatting, and weak descriptions"
      />
      <ResumeAnalyzer />
    </>
  );
}
