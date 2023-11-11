rm(list = ls())

library(tidyverse)
library(data.table)
library(umap)
library(Rtsne)

data_path <- "/Users/cordioli/dev/junction2023/data/Indoor/Participant_1/processed_with_sentiment.csv"

d <- fread(data_path)

# Plot m0-5 for left and right eye
d_left <- d %>% 
  select(time = left_ticktime_standardized, left_m_0:left_m_5) %>% 
  pivot_longer(left_m_0:left_m_5)
  
ggplot(d_left, aes(x = time, y = value)) +
  geom_line() +
  facet_grid(name~.)

d_right <- d %>% 
  select(time = left_ticktime_standardized, right_m_0:right_m_5) %>% 
  pivot_longer(right_m_0:right_m_5)

ggplot(d_right, aes(x = time, y = value)) +
  geom_line() +
  facet_grid(name~.)


# PCA using m0,m2, m3 and m5 only
# Discard all time frames with no sentiment classification
d_nna <- d %>% 
  filter(sentiment != "")

d_lr <- d_nna %>%  
   select(sentiment, all_of(ends_with(c("m_0", "m_2", "m_3", "m_5")))) %>% 
   mutate(across(ends_with(c("m_0", "m_2", "m_3", "m_5")), ~ as.numeric(scale(.))))

pca_all <- as.data.frame(prcomp(d_lr %>% select(-sentiment))$x[, 1:8]) %>% 
  mutate(sentiment = d_nna$sentiment)

pca_all_long = pca_all %>%
  pivot_longer(cols = PC1:PC8)

# Plot PCs densities
palette <- c("#D55E00", "#808080", "#56B4E9")

ggplot(pca_all_long, aes(x = value, fill = sentiment, color = sentiment)) + 
  geom_density(alpha = 0.3) + 
  facet_wrap(name ~ ., nrow = 3) + 
  theme_minimal() + 
  theme(legend.position = "top") + 
  labs(fill = "", color = "")+
  scale_color_manual(values = palette)

# Plot PC1-2
ggplot(pca_all, aes(x = PC1, y = PC2, color = sentiment)) +
  geom_point(alpha = .2) +
  scale_color_manual(values = palette)
  
# Plot PC1-2, only negative and positive sentiments
palette2 <- c("#D55E00","#56B4E9")

ggplot(pca_all %>% filter(sentiment != "NEUTRAL"), aes(x = PC1, y = PC2, color = sentiment)) +
  geom_point(alpha = .2) +
  scale_color_manual(values = palette2)


# UMAP viz
umap_all <- umap(d_lr %>% select(-sentiment))

umap_df <- data.frame(x = umap_all$layout[,1],
                      y = umap_all$layout[,2],
                      sentiment = d_lr$sentiment)

ggplot(umap_df, aes(x = x, y = y, color = sentiment)) +
  geom_point(alpha = .2) +
  scale_color_manual(values = palette2)

ggplot(umap_df %>% filter(sentiment != "NEUTRAL"), aes(x = x, y = y, color = sentiment)) +
  geom_point(alpha = .2) +
  scale_color_manual(values = palette2)

# tSNE viz
tsne_all <- Rtsne(d_lr %>% select(-sentiment))

tsne_df <- data.frame(x = tsne_all$Y[,1],
                      y = tsne_all$Y[,2],
                      sentiment = d_lr$sentiment)

ggplot(tsne_df, aes(x = x, y = y, color = sentiment)) +
  geom_point(alpha = .2) +
  scale_color_manual(values = palette)

ggplot(tsne_df %>% filter(sentiment != "NEUTRAL"), aes(x = x, y = y, color = sentiment)) +
  geom_point(alpha = .2) +
  scale_color_manual(values = palette2)

# # Smoothing with roll mean
# d_nna <- d %>% 
#   filter(sentiment != "")
# 
# d_lr <- d_nna %>% 
#   select(sentiment, all_of(ends_with(c("m_0", "m_2", "m_3", "m_5")))) %>% 
#   mutate(across(ends_with(c("m_0", "m_2", "m_3", "m_5")), ~ frollmean(.,n=100))) %>% 
#   filter(complete.cases(.))
# 
# pca_all <- as.data.frame(prcomp(d_lr %>% select(-sentiment), scale. = T)$x[, 1:8]) %>% 
#   mutate(sentiment = d_lr$sentiment)
# 
# pca_all_long = pca_all %>%
#   pivot_longer(cols = PC1:PC8)
# 
# ggplot(pca_all_long, aes(x = value, fill = sentiment, color = sentiment)) + 
#   geom_density(alpha = 0.3) + 
#   facet_wrap(name ~ ., nrow = 3) + 
#   theme_minimal() + 
#   theme(legend.position = "top") + 
#   labs(fill = "", color = "")
# 
# 
# ggplot(pca_all %>% filter(sentiment != "NEUTRAL"), aes(x = PC1, y = PC2, color = sentiment)) +
#   geom_point(alpha = .2)
# 
# ggplot(pca_all %>% filter(sentiment != "NEUTRAL"), aes(x = PC2, y = PC3, color = sentiment)) +
#   geom_point()