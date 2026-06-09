using System.Collections.Generic;

namespace ResumeAnalyser.Client.Models
{
    public class AnalysisResult
    {
        public int MatchScore { get; set; } = 0;
        public string MatchLabel { get; set; } = "Needs Work";
        public List<string> MatchedKeywords { get; set; } = new();
        public List<string> MissingKeywords { get; set; } = new();
        public List<string> Recommendations { get; set; } = new();
        public Dictionary<string, int> SkillScores { get; set; } = new();
        public string Summary { get; set; } = string.Empty;
    }
}
