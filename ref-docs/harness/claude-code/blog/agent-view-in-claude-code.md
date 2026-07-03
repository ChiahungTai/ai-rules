Agent view in Claude Code | Claude by Anthropic
Explore here
Agent view in Claude Code
Category
Product announcements
Product
Claude Code
Date
May 11, 2026
Reading time
5
min
Share
Copy link
https://claude.com/blog/agent-view-in-claude-code
Today we're introducing agent view in Claude Code: one place to manage all your Claude Code sessions.
When running agents in parallel before, you've probably had to manage multiple terminal tabs, a tmux grid, and an overloaded mental ledger of what you need to tackle next.
With agent view in Claude Code, you can kick off new agents, send them to the background, and jump in only when Claude needs you. See at a glance which agents are waiting on you, which are still working, and which are done, so you can easily steer many all at once.
How it works
Agent view improves visualizing and interacting with your Claude Code sessions in the CLI.
See everything at once
Press the left arrow from any session or run claude agents from the terminal to open agent view. Each row shows the session, whether it needs your input, the contents of its last response, and when you last interacted with it.
Peek and reply without leaving
Select a session to peek at the last turn. If a session is waiting on a decision, answer inline and the session picks back up. Press enter to attach directly to sessions where you want to explore the full transcript.
Background anything
Lastly, users can take any existing session and add it to agent view using /bg or skip the foreground entirely using claude --bg [task] to launch a fresh session.
How developers are using agent view
A few patterns we have seen from early users:
Scaling the number of concurrent sessions: Dispatch several ideas at once, each optionally paired with a skill, and return to a list of pull requests ready for review.
Manage long running agents: PR babysitters, dashboard updaters, and other looping jobs show their next run time right in the list.
Navigate between separate sessions: When you’re in the middle of a session, press the left arrow, start a related task or quick codebase question, then arrow right back into what you were doing. Peek shows the answer when it lands.
See what shipped: Status indicators on each row plus the title in peek make it easy to scan which sessions produced a PR.
Getting started
Agent view is available today as a Research Preview on Pro, Max, Team, Enterprise, and Claude API plans. Opt-in by running claude agents. Usual rate limits apply. See the docs for more information.
No items found.
PrevPrev
0/5
NextNext
eBook
FAQ
No items found.
Get Claude Code
curl -fsSL https://claude.ai/install.sh | bash
Copy command to clipboard
irm https://claude.ai/install.ps1 | iex
Copy command to clipboard
Or read the documentation
Try Claude Code
Try Claude CodeTry Claude Code
Developer docs
Developer docsDeveloper docs
Related posts
Explore more product news and best practices for teams building with Claude.
Jul 2, 2026
Giving admins more visibility and control over Claude spend
Product announcements
Giving admins more visibility and control over Claude spendGiving admins more visibility and control over Claude spend
Giving admins more visibility and control over Claude spendGiving admins more visibility and control over Claude spend
Jun 29, 2026
Introducing the Claude apps gateway for Amazon Bedrock and Google Cloud
Product announcements
Introducing the Claude apps gateway for Amazon Bedrock and Google CloudIntroducing the Claude apps gateway for Amazon Bedrock and Google Cloud
Introducing the Claude apps gateway for Amazon Bedrock and Google CloudIntroducing the Claude apps gateway for Amazon Bedrock and Google Cloud
Jun 29, 2026
Claude in Microsoft Foundry is now generally available
Product announcements
Claude in Microsoft Foundry is now generally availableClaude in Microsoft Foundry is now generally available
Claude in Microsoft Foundry is now generally availableClaude in Microsoft Foundry is now generally available
Jun 17, 2026
Secure access to the Claude Platform with Workload Identity Federation
Product announcements
Secure access to the Claude Platform with Workload Identity FederationSecure access to the Claude Platform with Workload Identity Federation
Secure access to the Claude Platform with Workload Identity FederationSecure access to the Claude Platform with Workload Identity Federation
Transform how your organization operates with Claude
See pricing
See pricingSee pricing
Contact sales
Contact salesContact sales
Get the developer newsletter
Product updates, how-tos, community spotlights, and more. Delivered monthly to your inbox.
Thank you! You’re subscribed.
Sorry, there was a problem with your submission, please try again later.
HomepageHomepage
Thank you! Your submission has been received!
Oops! Something went wrong while submitting the form.
Write
Button TextButton Text
Learn
Button TextButton Text
Code
Button TextButton Text
Write
Help me develop a unique voice for an audience
Hi Claude! Could you help me develop a unique voice for an audience? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Improve my writing style
Hi Claude! Could you improve my writing style? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Brainstorm creative ideas
Hi Claude! Could you brainstorm creative ideas? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Learn
Explain a complex topic simply
Hi Claude! Could you explain a complex topic simply? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Help me make sense of these ideas
Hi Claude! Could you help me make sense of these ideas? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Prepare for an exam or interview
Hi Claude! Could you prepare for an exam or interview? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Code
Explain a programming concept
Hi Claude! Could you explain a programming concept? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Look over my code and give me tips
Hi Claude! Could you look over my code and give me tips? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Vibe code with me
Hi Claude! Could you vibe code with me? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to— like Google Drive, web search, etc.—if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can—an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
More
Write case studies
This is another test
Write grant proposals
Hi Claude! Could you write grant proposals? If you need more information from me, ask me 1-2 key questions right away. If you think I should upload any documents that would help you do a better job, let me know. You can use the tools you have access to — like Google Drive, web search, etc. — if they’ll help you better accomplish this task. Do not use analysis tool. Please keep your responses friendly, brief and conversational. Please execute the task as soon as you can - an artifact would be great if it makes sense. If using an artifact, consider what kind of artifact (interactive, visual, checklist, etc.) might be most helpful for this specific task. Thanks for your help!
Write video scripts
this is a test
AnthropicAnthropic
© [year] Anthropic PBC
Products
Claude
ClaudeClaude
Claude Code
Claude CodeClaude Code
Claude Code for Enterprise
Claude Code for EnterpriseClaude Code for Enterprise
Claude Cowork
Claude CoworkClaude Cowork
@Claude
@Claude@Claude
Claude Design
Claude DesignClaude Design
Claude Science
Claude ScienceClaude Science
Claude Security
Claude SecurityClaude Security
Download app
Download appDownload app
Pricing
PricingPricing
Log in
Log inLog in
Features
Claude for Chrome
Claude for ChromeClaude for Chrome
Claude for Microsoft 365
Claude for Microsoft 365Claude for Microsoft 365
Skills
SkillsSkills
Models
Mythos
MythosMythos
Fable
FableFable
Opus
OpusOpus
Sonnet
SonnetSonnet
Haiku
HaikuHaiku
Solutions
AI agents
AI agentsAI agents
Code modernization
Code modernizationCode modernization
Coding
CodingCoding
Customer support
Customer supportCustomer support
Education
EducationEducation
Enterprise
EnterpriseEnterprise
Financial services
Financial servicesFinancial services
Government
GovernmentGovernment
Healthcare
HealthcareHealthcare
Legal
LegalLegal
Life sciences
Life sciencesLife sciences
Nonprofits
NonprofitsNonprofits
Security
SecuritySecurity
Small business
Small businessSmall business
Claude Platform
Overview
OverviewOverview
Developer docs
Developer docsDeveloper docs
Pricing
PricingPricing
Ecosystem
EcosystemEcosystem
Marketplace
MarketplaceMarketplace
Claude on AWS
Claude on AWSClaude on AWS
Google Cloud
Google CloudGoogle Cloud
Microsoft Foundry
Microsoft FoundryMicrosoft Foundry
Regional compliance
Regional complianceRegional compliance
Console login
Console loginConsole login
Resources
Blog
BlogBlog
Claude partner network
Claude partner networkClaude partner network
Community
CommunityCommunity
Connectors
ConnectorsConnectors
Courses
CoursesCourses
Customer stories
Customer storiesCustomer stories
Engineering at Anthropic
Engineering at AnthropicEngineering at Anthropic
Events
EventsEvents
Plugins
PluginsPlugins
Powered by Claude
Powered by ClaudePowered by Claude
Service partners
Service partnersService partners
Tutorials
TutorialsTutorials
Use cases
Use casesUse cases
Company
Anthropic
AnthropicAnthropic
Careers
CareersCareers
Policy
PolicyPolicy
Economic Futures
Economic FuturesEconomic Futures
Research
ResearchResearch
News
NewsNews
Policy on the AI Exponential
Policy on the AI ExponentialPolicy on the AI Exponential
Responsible Scaling Policy
Responsible Scaling PolicyResponsible Scaling Policy
Security and compliance
Security and complianceSecurity and compliance
Transparency
TransparencyTransparency
Programs
Startups
StartupsStartups
Research Labs
Research LabsResearch Labs
Help and security
Availability
AvailabilityAvailability
Status
StatusStatus
Support center
Support centerSupport center
Terms and policies
Privacy choices
Cookie settings
We use cookies to deliver and improve our services, analyze site usage, and if you agree, to customize or personalize your experience and market our services to you. You can read our Cookie Policy here.
Customize cookie settings
Reject all cookies
Accept all cookies
Save preferences
Privacy policy
Privacy policyPrivacy policy
Responsible disclosure policy
Responsible disclosure policyResponsible disclosure policy
Terms of service: Commercial
Terms of service: CommercialTerms of service: Commercial
Terms of service: Consumer
Terms of service: ConsumerTerms of service: Consumer
Usage policy
Usage policyUsage policy
x.comx.com
LinkedInLinkedIn
YouTubeYouTube
InstagramInstagram
English (US)
Claude Code
Coding
Productivity
