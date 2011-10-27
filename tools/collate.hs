{-
Collate review scores.

Given a file containing a list of reviews the following form:

--------------
1.  Author <email>
    "Title"

<reviewer 1 initials>: (strong|weak)? (accept|reject)
    Comments

<reviewer 2 initials>: (strong|weak)? (accept|reject)
    Comments

...
--------------

Generates a summary of the scores for each paper, assigning 2 points for a
strong accept and -2 points to a strong reject.

-}

import Text.Regex
import Data.List
import Data.Maybe
import Text.Printf
import Data.Function
import Data.Ord
import Data.Char
import Debug.Trace
import System.Environment

main = do
  [file] <- getArgs
  str <- readFile file
  let ls = lines str
      segs = splitPre "---" ls
      
      scored :: [(String,[(String,Score)])]
      scored = [ (n,scores ss) | 
                 (Just n, ss) <- zip (map findNum segs) segs ]

      totaled :: [(String,[(String,Score)],Int)]
      totaled = [ (n, ss, total (map snd ss)) | (n, ss) <- scored ]

      sorted = sortBy (flip (compare `on` thd3)) totaled

      thd3 (_,_,c) = c

  mapM_ (\(n,ss,t) -> do 
           printf "%s\n" n
           mapM_ (\(name,score) -> printf "   %20s: %s\n" name (showScore score)) ss
           printf "   %20s: %d\n" "Total" t
           printf "\n"
        ) sorted
  
total :: [Score] -> Int
total ss = sum scores
   where scores = [ i | Score i <- ss ]

splitPre :: String -> [String] -> [[String]]
splitPre pat []   = []
splitPre pat strs = 
  case break (pat `isPrefixOf`) strs of
     ([],  [])     -> []
     (seg, [])     -> [seg]
     ([],  _:rest) -> splitPre pat rest
     (seg, _:rest) -> seg : splitPre pat rest

findNum :: [String] -> Maybe String
findNum = listToMaybe . catMaybes . map getNum
  where getNum s = case matchRegex (mkRegex "^([0-9]+\\..*)$") s of
                     Nothing -> Nothing
                     Just (line:_) -> Just line

data Score = Score Int | Conflicted | None
  deriving (Eq, Show)

showScore (Score i) = show i
showScore Conflicted = "Conflicted"
showScore None = "--"

scores :: [String] -> [(String,Score)]
scores = catMaybes . map getScore
  where getScore s = case matchRegex (mkRegex "^([A-Z]+): (([Ww]eak|[Ss]trong)? *([Aa]ccept|[Rr]eject))") s of
                       Nothing -> Nothing
                       Just (name:eval:_) -> Just (name, Score score)
                          where score = case map toLower eval of
                                          "strong accept" -> 2
                                          "accept" -> 2
                                          "weak accept" -> 1
                                          "weak reject" -> -1
                                          "reject" -> -2


--                       Just (name:"N":_) -> Just (name, None)
--                       Just (name:"C":_) -> Just (name, Conflicted)
--                       Just (name:score:_) -> Just (name, Score (read score :: Int))
