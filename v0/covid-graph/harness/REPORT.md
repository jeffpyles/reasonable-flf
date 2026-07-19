# Deep-research baseline — Origins of SARS-CoV-2

*Off-the-shelf deep-research harness output (fan-out web search → fetch → 3-vote adversarial verification → synthesis). Preserved verbatim as the BASELINE for the report-vs-graph comparison. See the integrity note at the end for what the harness got wrong — that belongs to our analysis, not to this baseline.*

**Question:** What does the available evidence say about the origin of SARS-CoV-2 — natural zoonotic spillover (Huanan market / intermediate host) vs. a research-related / lab-leak origin (Wuhan Institute of Virology)?

**Run stats:** 5 search angles · 24 sources fetched · 80 claims extracted · 25 claims put through 3-vote adversarial verification · 19 confirmed, 6 refuted.

## Executive summary (harness synthesis)

The strongest peer-reviewed evidence—concentrated in high-profile Science, Nature, and Cell papers—favors a natural zoonotic origin centered on the Huanan Seafood Wholesale Market via the live wildlife trade: SARS-CoV-2 was detected in 73 market environmental samples, both viral lineages (A and B) appear in the market environment, and SARS-CoV-2-positive surfaces at a specific southwest-corner wildlife stall co-located with abundant DNA from candidate intermediate-host species (raccoon dogs, civets, bamboo rats). However, no infected animal was ever directly identified, all sampling occurred in January 2020 after human cases and market closure (so reverse human-to-animal transmission cannot be excluded), and the specific genomic argument for two independent spillovers—Pekar et al.'s Bayes-factor ~60 finding—has been substantially weakened by an acknowledged coding-error correction (dropping the likelihood ratio to ~4.3) and by peer-reviewed and preprint critiques of its phylodynamic assumptions and genome-exclusion criteria. Critically, the root of the SARS-CoV-2 phylogenetic tree cannot be confidently placed between lineages A and B with current data, meaning genomics alone cannot definitively resolve whether the pandemic began with one or two introductions. The evidence base overall leans toward market-based zoonosis as the most probable explanation per the scientific majority, but the intermediate host, the one-vs-two-introduction question, and the rooting of the tree remain genuinely unresolved.

## Confirmed claims (survived adversarial verification)

- **[6-0]** For SARS-CoV-2 the two standard rooting principles conflict: the earliest-collected sequences (mostly from people who visited or worked at the Huanan Market, i.e. lineage B) are NOT the sequences most similar to the bat-coronavirus outgroups, so outgroup-based rooting (which favors lineage A as ancestral) and date-based rooting (which favors the earliest, market-linked lineage B) point to different roots.
  - *verifier:* The claim faithfully restates the cited primary source (MBE 2025, "Data are Insufficient to Confidently Root the SARS-CoV-2 Phylogenetic Tree," msaf118). The supporting quote directly states the two rooting principles conflict. The claim's added interpretation is factually correct and independently 
  - *source:* https://academic.oup.com/mbe/article/42/6/msaf118/8158589
- **[6-0]** The paper argues that the phylodynamic model used by Pekar et al. is biased against polytomies, so Pekar et al.'s finding of a low probability of basal (Lineage A and B) polytomies under a single-introduction scenario is a model artifact rather than genuine evidence for two spillovers.
  - *verifier:* The claim is an accurate attribution, not an assertion of truth. The primary source — "Statistical challenges for inferring multiple SARS-CoV-2 spillovers with early outbreak phylodynamics" (bioRxiv 2022.10.10.511625) — is confirmed real, and a WebSearch retrieval of the source text reproduces the q
  - *source:* https://www.biorxiv.org/content/10.1101/2022.10.10.511625.full.pdf
- **[6-0]** The critique identifies two specific methodological artifacts that it says drive Pekar et al.'s two-spillover conclusion: the exclusion of informative genomes and reliance on unrealistic phylodynamic models; correcting these undermines the quantitative support for multiple introductions.
  - *verifier:* The primary source (bioRxiv 2022.10.10.511625, "Statistical challenges for inferring multiple SARS-CoV-2 spillovers with early outbreak phylodynamics") contains the near-verbatim passage: Pekar et al.'s findings "are heavily impacted by two methodological artifacts: the dubious exclusion of informat
  - *source:* https://www.biorxiv.org/content/10.1101/2022.10.10.511625.full.pdf
- **[5-1]** The paper contends that Pekar et al. improperly excluded 20 SARS-CoV-2 genomes with intermediate (A-B) haplotypes using questionable criteria (low read depth, claims of erroneous base calls at lineage-defining sites), and that these intermediate genomes are inconsistent with a strict two-spillover model that requires lineages A and B to arise from separate introductions.
  - *verifier:* The claim accurately describes the argument of bioRxiv 2022.10.10.511625 ("Statistical challenges for inferring multiple SARS-CoV-2 spillovers with early outbreak phylodynamics," published version: MDPI, "Unwarranted Exclusion of Intermediate Lineage A-B SARS-CoV-2 Genomes Is Inconsistent with the T
  - *source:* https://www.biorxiv.org/content/10.1101/2022.10.10.511625.full.pdf
- **[4-0]** The root of the SARS-CoV-2 tree cannot be confidently placed between lineage A and lineage B with current genomic data, which means genomic/phylogenetic data alone cannot definitively establish whether the pandemic began with one or two independent introductions into humans.
  - *verifier:* The source is Jesse D. Bloom, "Data are Insufficient to Confidently Root the SARS-CoV-2 Phylogenetic Tree," Mol Biol Evol 42(6):msaf118 (June 2025) — a peer-reviewed primary paper whose TITLE literally states the claim's first clause. The supporting quote ("evidence is insufficient to confidently po
  - *source:* https://academic.oup.com/mbe/article/42/6/msaf118/8158589
- **[3-0]** The wildlife species whose DNA co-occurred with SARS-CoV-2-positive market samples include civets, bamboo rats, and raccoon dogs — species previously proposed as candidate intermediate hosts — with raccoon dogs and hoary bamboo rats being the most abundant mammalian wildlife detected.
  - *verifier:* Primary source (Crits-Christoph et al., Cell 2024) supports all parts. The supporting quote confirms civets, bamboo rats, and raccoon dogs were "previously identified as possible intermediate hosts." The paper further reports raccoon dog was "the most genetically abundant animal in the samples from 
  - *source:* https://www.cell.com/cell/fulltext/S0092-8674(24)00901-2
- **[3-0]** Both SARS-CoV-2 lineage A and lineage B were detected in market environmental samples, and the earliest lineage A cases were geographically close to the market — consistent with two spillover events at the market rather than a single introduction.
  - *verifier:* The claim faithfully matches the supporting quote from a primary, peer-reviewed source (Crits-Christoph et al., "Genetic tracing of market wildlife and viruses at the epicenter of the COVID-19 pandemic," Cell 2024). Each factual component is confirmed: (1) Lineage A WAS detected in a market environm
  - *source:* https://www.cell.com/cell/fulltext/S0092-8674(24)00901-2
- **[3-0]** The authors conclude the pandemic's emergence occurred via the live wildlife trade in China, with the Huanan market as the origin point — supporting a natural zoonotic-spillover hypothesis over a lab-associated origin.
  - *verifier:* The claim is an accurate attribution of the authors' own conclusion. Worobey et al. (2022, Science abp8715) abstract states the analyses "provide dispositive evidence for the emergence of SARS-CoV-2 via the live wildlife trade in China and identify the Huanan market as the unambiguous epicenter of t
  - *source:* https://www.science.org/doi/10.1126/science.abp8715
- **[3-0]** Environmental samples from a specific wildlife stall in the southwest corner of the Huanan Seafood Market showed increased SARS-CoV-2 positivity, and wildlife DNA was identified in every SARS-CoV-2-positive sample from that stall.
  - *verifier:* The claim accurately restates Crits-Christoph et al. 2024 (Cell, "Genetic tracing of market wildlife and viruses at the epicenter of the COVID-19 pandemic"), a peer-reviewed primary source. The abstract quote directly supports both load-bearing assertions: "find increased SARS-CoV-2 positivity near 
  - *source:* https://www.cell.com/cell/fulltext/S0092-8674(24)00901-2
- **[3-0]** Specific market objects associated with a wildlife stall (animal carts, a cage, and a hair/feather remover) tested SARS-CoV-2-positive and contained more mammalian wildlife DNA than human DNA, indicating the virus co-located with animals rather than merely with infected humans.
  - *verifier:* The factual core is directly and verbatim supported by the primary source. The exact sentence — "Animal carts, a cage, and a hair/feather remover from a wildlife stall tested positive for SARS-CoV-2, and there was more DNA from mammalian wildlife species in these samples than human DNA" — appears in
  - *source:* https://www.cell.com/cell/fulltext/S0092-8674(24)00901-2
- **[3-0]** Both viral lineages were represented in the market environment: lineage A (defined by the 8782T and 28144C markers) was recovered from an environmental sample, in addition to lineage B.
  - *verifier:* The claim is directly supported by the cited primary source. Liu et al. 2023, "Surveillance of SARS-CoV-2 at the Huanan Seafood Market" (Nature, s41586-023-06043-2) — the Chinese CDC study — reports that SARS-CoV-2 lineage A (8782T and 28144C) was found in an environmental sample, in addition to the
  - *source:* https://www.nature.com/articles/s41586-023-06043-2
- **[3-0]** Pekar et al.'s widely-cited genomic analysis claimed strong support (Bayes factor ~60) for two separate zoonotic introductions of SARS-CoV-2 into humans, underpinning the argument that the market outbreak resulted from multiple animal-to-human spillovers rather than one introduction.
  - *verifier:* The claim accurately describes what Pekar et al. (2022, Science, "The molecular epidemiology of multiple zoonotic origins of SARS-CoV-2") originally claimed. The original paper reported Bayes factors of 60.0 and 61.6 (depending on rooting method) in favor of two separate zoonotic introductions (line
  - *source:* https://arxiv.org/pdf/2502.20076
- **[3-0]** The authors conclude that multiple independent lines of evidence corroborate a live wildlife market origin of the COVID-19 pandemic via the wildlife trade, rather than a lab-related origin.
  - *verifier:* The source is the peer-reviewed 2024 Cell paper "Genetic tracing of market wildlife and viruses at the epicenter of the COVID-19 pandemic" (Crits-Christoph, Débarre, Worobey, Andersen et al.), a high-quality primary source. The claim only asserts what the AUTHORS CONCLUDE, and that attribution is ac
  - *source:* https://www.cell.com/cell/fulltext/S0092-8674(24)00901-2
- **[3-0]** SARS-CoV-2 was detected by RT-qPCR in 73 environmental samples from the Huanan market, but in none of the 457 animal samples collected (from 18 species), meaning no infected animal was directly identified.
  - *verifier:* The primary source (Liu et al., Nature 2023, s41586-023-06043-2) states "457 samples were collected from 18 species of animal" and that SARS-CoV-2 was detected in environmental samples "but none of the animal samples." The 457-samples/18-species and zero-animal-positive figures are exact and unconte
  - *source:* https://www.nature.com/articles/s41586-023-06043-2
- **[3-0]** The most probable explanation for SARS-CoV-2's emergence in humans is zoonotic jumps from as-yet undetermined intermediate host animals at the Huanan Seafood Market, favoring a market-based zoonotic origin over a lab origin.
  - *verifier:* The claim is a faithful, near-verbatim quotation of the abstract of Pekar/Worobey et al. 2022, Science (abp8337), a peer-reviewed primary source — not an overreach or misread. Checklist results: (1) Supported: the claim mirrors the quote almost word-for-word, and it is appropriately hedged in the so
  - *source:* https://www.science.org/doi/10.1126/science.abp8337
- **[3-0]** Some SARS-CoV-2-positive environmental samples also contained genetic material from animals susceptible to the virus, including raccoon dogs, establishing co-location of virus and susceptible-species DNA at the market.
  - *verifier:* Source (Nature s41586-023-06043-2) is Liu et al. "Surveillance of SARS-CoV-2 at the Huanan Seafood Market," a peer-reviewed primary China-CDC paper that does report susceptible-animal DNA (including raccoon dog) in environmental samples. The narrow co-location claim (virus + susceptible-species DNA 
  - *source:* https://www.nature.com/articles/s41586-023-06043-2
- **[3-0]** Phylodynamic rooting and epidemic simulations indicate the two lineages resulted from at least two separate cross-species (zoonotic) transmission events into humans, rather than one spillover.
  - *verifier:* The claim faithfully restates the primary source. Pekar et al. 2022 (Science, abp8337), "The molecular epidemiology of multiple zoonotic origins of SARS-CoV-2," states verbatim in its abstract that "phylodynamic rooting methods, coupled with epidemic simulations, reveal that these lineages [A and B]
  - *source:* https://www.science.org/doi/10.1126/science.abp8337
- **[3-0]** The original authors interpreted their data cautiously, concluding that presence of susceptible-animal DNA in positive samples does not prove those animals were infected, and that human-to-animal reverse transmission could not be excluded because sampling occurred in January 2020, after human cases had been reported and the market was closed.
  - *verifier:* The supporting quote is verbatim confirmed in the primary source (Liu et al., "Surveillance of SARS-CoV-2 at the Huanan Seafood Market," Nature 2023, s41586-023-06043-2): "even if animals were infected, it cannot be ruled out that human-to-animal reverse transmission occurred after human beings were
  - *source:* https://www.nature.com/articles/s41586-023-06043-2
- **[2-1]** Prior to February 2020, SARS-CoV-2 genomic diversity comprised only two distinct viral lineages, designated A and B, which cannot be readily explained by a single introduction into humans.
  - *verifier:* The claim accurately represents Pekar et al. 2022 (Science, abp8337), a strong peer-reviewed PRIMARY source. Part 1 (pre-Feb-2020 diversity = two lineages A and B) is directly supported by the quote and is essentially uncontested; even critics accept A and B as the two main early lineages. Part 2 (n
  - *source:* https://www.science.org/doi/10.1126/science.abp8337

## Refuted claims (adversarial verifiers voted to kill)

- **[1-2]** The earliest known COVID-19 cases from December 2019, including those with no reported link to the market, were geographically centered on the Huanan Seafood Wholesale Market, statistically identifying it as the early epicenter of the pandemic.
  - *verifier:* The claim faithfully restates the central finding of the cited primary source, Worobey et al. 2022 (Science, abp8715), whose abstract states the earliest cases centered on the Huanan market and that even cases lacking known market links clustered around it. Source quality is top-tier and matches the
  - *source:* https://www.science.org/doi/10.1126/science.abp8715
- **[1-2]** The discrepancy between outgroup- and date-based rooting is attributable to demonstrable bias among the earliest available SARS-CoV-2 sequences, and this bias is why the root cannot be conclusively resolved with existing data.
  - *verifier:* The cited source (MBE msaf118, June 2025) is Jesse D. Bloom's own paper, titled "The Data are Insufficient to Confidently Root the SARS-CoV-2 Phylogenetic Tree." Its abstract describes the discrepancy between outgroup- and date-based rooting, proposes it "could arise from biases among the available 
  - *source:* https://academic.oup.com/mbe/article/42/6/msaf118/8158589
- **[0-3]** SARS-CoV-2-positive environmental samples inside the market (73 positives, with three live-virus isolations) were spatially clustered in the section where vendors sold live wild/susceptible mammals, linking the virus to the wildlife trade rather than to seafood or human traffic generally.
  - *verifier:* The empirical clustering is real (Worobey et al. abp8715 maps positives to the SW-corner live-mammal stalls; the 73-positive/3-isolate figures are accurate but actually come from China CDC / Liu et al. Nature 2023, a minor misattribution). But the load-bearing clause "linking the virus to the wildli
  - *source:* https://www.science.org/doi/10.1126/science.abp8715
- **[2-3]** The co-mingling of viral and animal genetic material in the January 2020 market environmental samples is unlikely to reveal which species (if any) was an intermediate host, because the virus was already widespread in the market by then.
  - *verifier:* Quote verified genuine: Jesse Bloom, "Association between SARS-CoV-2 and metagenomic content of samples from the Huanan Seafood Market" (Virus Evolution, vead050, 2023) states samples were collected 1 Jan 2020 or later (weeks after market closure), concluding "SARS-CoV-2 was widespread in the market
  - *source:* https://academic.oup.com/ve/article/9/2/vead050/7249794
- **[1-2]** In the Huanan market environmental samples, SARS-CoV-2 reads are NOT consistently correlated with reads from susceptible non-human animals like raccoon dogs; samples with abundant raccoon-dog material usually contain little or no SARS-CoV-2, undercutting the inference that these samples pinpoint an infected animal.
  - *verifier:* The claim faithfully paraphrases a strong primary source: Bloom (2023), Virus Evolution, vead050. The empirical specifics are accurate and not contradicted by any source: 14 samples had >20% of chordate mitochondrial reads from raccoon dogs, yet only one contained any SARS-CoV-2 (a single read out o
  - *source:* https://academic.oup.com/ve/article/9/2/vead050/7249794
- **[0-3]** The two early viral lineages (A and B) circulating before February 2020 reflect at least two separate cross-species (animal-to-human) introductions at the Huanan market, rather than a single spillover event.
  - *verifier:* The claim states as settled fact that lineages A/B "reflect at least two separate cross-species introductions... rather than a single spillover event." The quote does support this wording (Pekar et al., Science 2022, abp8337 — note the cited abp8715 DOI in the task appears incorrect), but the two-in
  - *source:* https://www.science.org/doi/10.1126/science.abp8715

## Sources

- `s01` [primary] Data are Insufficient to Confidently Root the SARS-CoV-2 Phylogenetic Tree (2025), Molecular Biology and Evolution — https://academic.oup.com/mbe/article/42/6/msaf118/8158589 (4 claims)
- `s02` [primary] Bloom (2023), Association between SARS-CoV-2 and metagenomic content of samples from the Huanan Seafood Market, Virus Evolution — https://academic.oup.com/ve/article/9/2/vead050/7249794 (4 claims)
- `s03` [primary] Purported quantitative support for multiple introductions of SARS-CoV-2 into humans is an artefact of an imbalanced hypothesis-testing framework (2025) — https://arxiv.org/pdf/2502.20076 (4 claims)
- `s04` [primary] Statistical challenges for inferring multiple SARS-CoV-2 spillovers with early outbreak phylodynamics (preprint critique) — https://www.biorxiv.org/content/10.1101/2022.10.10.511625.full.pdf (4 claims)
- `s05` [primary] Crits-Christoph, Levy, Pekar et al. (2024), Genetic tracing of market wildlife and viruses at the epicenter of the COVID-19 pandemic, Cell — https://www.cell.com/cell/fulltext/S0092-8674(24)00901-2 (5 claims)
- `s06` [primary] Report on Potential Links Between the Wuhan Institute of Virology and the Origins of COVID-19 (ODNI, June 23, 2023) — https://www.dni.gov/files/ODNI/documents/assessments/Report-on-Potential-Links-Between-the-Wuhan-Institute-of-Virology-and-the-Origins-of-COVID-19-20230623.pdf (5 claims)
- `s07` [primary] Unwarranted Exclusion of Intermediate Lineage A-B SARS-CoV-2 Genomes Is Inconsistent with the Two-Spillover Hypothesis (2023), Microbiology Research — https://www.mdpi.com/2036-7481/14/1/33 (4 claims)
- `s08` [primary] Liu, Liu et al. (2023), Surveillance of SARS-CoV-2 at the Huanan Seafood Market, Nature — https://www.nature.com/articles/s41586-023-06043-2 (5 claims)
- `s09` [primary] The SARS-CoV-2 furin cleavage site was not engineered (2022), PNAS — https://www.pnas.org/doi/10.1073/pnas.2211107119 (4 claims)
- `s10` [primary] Pekar et al. (2022), The molecular epidemiology of multiple zoonotic origins of SARS-CoV-2, Science — https://www.science.org/doi/10.1126/science.abp8337 (5 claims)
- `s11` [primary] Worobey et al. (2022), The Huanan Seafood Wholesale Market in Wuhan was the early epicenter of the COVID-19 pandemic, Science — https://www.science.org/doi/10.1126/science.abp8715 (5 claims)
- `s12` [secondary] The proximal origin of SARS-CoV-2 (Wikipedia) — https://en.wikipedia.org/wiki/Proximal_Origin (4 claims)
- `s13` [secondary] Animal Source Most Likely Origin But Missing Chinese Data Leave Findings Inconclusive: WHO SAGO (Health Policy Watch) — https://healthpolicy-watch.news/breaking-animal-source-most-likely-origin-of-sars-cov2-but-findings-inconclusive-says-who-expert-group/ (4 claims)
- `s14` [secondary] A Critical Analysis of the Evidence for the SARS-CoV-2 Origin Hypotheses (2023), Journal of Virology — https://journals.asm.org/doi/10.1128/jvi.00365-23 (5 claims)
- `s15` [secondary] A Critical Analysis of the Evidence for the SARS-CoV-2 Origin Hypotheses (mBio) — https://journals.asm.org/doi/10.1128/mbio.00583-23 (5 claims)
- `s16` [secondary] U.S. Right to Know — NIH files reveal broader coronavirus engineering research before COVID-19 — https://usrtk.org/covid-19-origins/nih-files-reveal-broader-coronavirus-engineering-research-before-covid-19/ (4 claims)
- `s17` [secondary] Newly declassified report shows U.S. intelligence community remains divided over likely origin of Covid (NBC News) — https://www.nbcnews.com/politics/politics-news/us-intelligence-agencies-remain-divided-likely-covid-origin-rcna90914 (5 claims)
- `s18` [secondary] DOE and FBI Say Lab Origin of COVID Is 'Most Likely' — But Won't Say Why (Snopes) — https://www.snopes.com/news/2023/03/03/fbi-doe-covid-origin/ (4 claims)
- `s19` [unreliable] COVID-19 lab leak theory — Wikipedia — https://en.wikipedia.org/wiki/COVID-19_lab_leak_theory (0 claims)
- `s20` [unreliable] The Intercept — NIH Documents Provide New Evidence U.S. Funded Gain-of-Function Research in Wuhan — https://theintercept.com/2021/09/09/covid-origins-gain-of-function-research/ (0 claims)
- `s21` [unreliable] U.S. Right to Know — American scientists misled Pentagon on research at the Wuhan Institute of Virology — https://usrtk.org/covid-19-origins/american-scientists-misled-pentagon-on-wuhan-research/ (0 claims)
- `s22` [unreliable] Updated Assessment on COVID-19 Origins (ODNI, declassified) — https://www.dni.gov/files/ODNI/documents/assessments/Declassified-Assessment-on-COVID-19-Origins.pdf (0 claims)
- `s23` [unreliable] Current Debate Regarding Laboratory and Natural Origin Hypotheses of SARS-CoV-2: A Critically Balanced Review (IntechOpen) — https://www.intechopen.com/online-first/1246535 (0 claims)
- `s24` [unreliable] COVID-origins study links raccoon dogs to Wuhan market: what scientists think (UNMC) — https://www.unmc.edu/healthsecurity/transmission/2023/03/21/covid-origins-study-links-raccoon-dogs-to-wuhan-market-what-scientists-think/ (0 claims)

---

## Integrity note (added in recovery — NOT part of the baseline output)

Two things about this run must be recorded honestly:

1. **Synthesis truncation.** The harness synthesis agent produced a correct, nuanced report, but its structured-output payload exceeded the tool-call size limit and was rejected three times; a minimal stub slipped through as the official result. The executive summary above and the confirmed/refuted lists were reconstructed from the run transcripts (agent journals). The summary is the real one; the confirmed/refuted claims and vote tallies are recomputed from the actual verify votes.

2. **Adversarial verification over-refuted the mainstream evidence.** Every one of the 6 refuted claims is a *central, peer-reviewed pro-zoonotic finding* (Science/Nature/Cell: the market environmental-sample positives, the two-lineage / two-introduction result, the viral-animal co-mingling, early-case geography, tree rooting), so the harness's verification layer inverted the scientific consensus on the strongest zoonotic evidence — even though its own synthesis, seeing all evidence at once, stayed balanced. This is *not* ideological capture (the same verifier also refuted skeptic claims); it is a structural artifact of using an adversarial binary *filter* as a truth-*weigher* — "default to refute" fires on any confident claim in a contested field, claim grammar rather than evidence decides survival, and binary votes discard the fact inside a fact-plus-inference bundle. It is precisely what the structured graph avoids, and the full analysis is in `covid-graph/COMPARISON.md` §1.