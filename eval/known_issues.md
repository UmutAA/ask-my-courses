- Cross-course contamination: query "late policy for CENG301" retrieves chunks 
  from CENG332 and CENG315 syllabi too, likely because course code isn't 
  present in the chunk text itself, only in metadata. To fix in Week 2 
  (chunking) by prepending course code/name to each chunk before embedding.