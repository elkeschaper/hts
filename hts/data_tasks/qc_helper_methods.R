library("ggplot2")
library("plyr")
require(grid)

# Pretty, but not perfect in case of red-green blindness:
#colors = c("darkblue", "blue", "turquoise", "green", "yellow", "red", "darkred")
#
#colors = c("darkblue", "blue", "turquoise", "green", "yellow", "magenta", "darkmagenta")

# Light orange to blue to black scale.
colors = c("black", "darkblue", "blue", "orangered3", "orange", "papayawhip")



tile_plot_x1x2 <- function(data, column, label, save){
data$x2 = factor(data$x2, levels = max(data$x2):min(data$x2))
data$x1 = factor(data$x1, levels = min(data$x1):max(data$x1))
data$tmp = data[,column]
p = ggplot(data, aes(x= x1, y= x2, fill=tmp), environment = environment()) 
p = p + geom_raster() + scale_fill_gradientn(colours = colors, name = column)
p = p + coord_fixed(ratio=1)
p = beautifier(p)
if (save == TRUE) {
ggsave(paste(pathImages, label, '_',column,'_x1x2.pdf', sep=''), width=12, height=8, dpi = 300)
}
return(p)
}

tile_plot_x1x2x3 <- function(data, column, save){
data$x2 = factor(data$x2, levels = max(data$x2):min(data$x2))
data$x1 = factor(data$x1, levels = min(data$x1):max(data$x1))
data$tmp = data[,column]
p = ggplot(data, aes(x= x1, y= x2, fill=tmp), environment = environment()) + facet_wrap(~x3)
p = p + geom_raster() + scale_fill_gradientn(colours = colors, name = column)
p = p + coord_fixed(ratio=1)
p = beautifier(p)
if (save == TRUE) {
ggsave(paste(pathImages, column, '_x1x2x3.pdf', sep=''), width=12, height=8, dpi = 300)
}
return(p)
}


get_label_positions <- function(x, thresholds){
  
  spread = diff(range(x))
  label_positions = (c(0, thresholds) + c(thresholds, 0))/2
  label_positions[[1]] = min(thresholds[[1]] - spread/10, min(x) + spread/5)
  label_positions[[length(label_positions)]] = max(thresholds[[length(thresholds)]] + spread/10, min(x) - spread/5)
  return(label_positions)
}



beautifier <- function(p){
p <- p + theme(panel.background = element_rect(fill = 'transparent', colour = NA),
#panel.grid.minor = element_blank(),panel.grid.major = element_blank(),
legend.background = element_rect(colour = "white"),
legend.text = element_text(family = "sans", size=10, face='italic', hjust=0),
legend.key = element_rect(colour = 'white', fill = 'white'),
strip.background = element_rect(fill = 'transparent', colour = NA), # colour='red', fill='#CCCCFF'
strip.text.x = element_text(family = "sans",size=10, angle = 0),
strip.text.y = element_text(family = "sans",size=10, angle = 270),
axis.text.x = element_text(family = "sans",size=9, angle = 90),
axis.text.y = element_text(family = "sans",size=9),
axis.ticks.length = unit(0.05, "cm"),
axis.ticks.margin= unit(0.05, "cm"), # 
plot.background = element_rect(fill = 'transparent', colour = NA)
)
return(p)
}

beautifier2 <- function(p){
p <- p + theme(panel.background = element_rect(fill = 'transparent', colour = NA),
#panel.grid.minor = element_blank(),panel.grid.major = element_blank(),
legend.background = element_rect(colour = "white"),
legend.text = element_text(family = "sans", size=10, face='italic', hjust=0),
legend.key = element_rect(colour = 'white', fill = 'white'),
strip.background = element_rect(fill = 'transparent', colour = NA), # colour='red', fill='#CCCCFF' 
plot.background = element_rect(fill = 'transparent', colour = NA)
)
return(p)
}

lm_eqn = function(m) {
  
  l <- list(a = format(coef(m)[1], digits = 2),
            b = format(abs(coef(m)[2]), digits = 2),
            r2 = format(summary(m)$r.squared, digits = 3));
  
  if (coef(m)[2] >= 0)  {
    eq <- substitute(italic(y) == a + b %.% italic(x)*","~~italic(r)^2~"="~r2,l)
  } else {
    eq <- substitute(italic(y) == a - b %.% italic(x)*","~~italic(r)^2~"="~r2,l)    
  }
  
  as.expression(eq);                 
}