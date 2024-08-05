#include <gsl/gsl_blas.h>
#include <gsl/gsl_vector.h>
#include <gsl/gsl_matrix.h>
#include <stdbool.h>
#include "lbfgs.h"
#include "const.h"

typedef struct
{
    gsl_vector* Z;         /* A m matrix corresponding to the system matrix of observation equation */
    float H;            /* A 1*1 matrix corresponding to observational disturbances epsilon      */
    gsl_matrix* T;          /* A m x m matrix corresponding to the first system matrix of state equation. */
    gsl_matrix* Q;           /* A m*m matrix for the state disturbance covariance*/
    int m;
    int structure; /* 100: 4 month, 10: semi-annual; 1: annual */
} ssmodel_constants;


/* non-diffuse filtering for missing obs */
void filter1step_missingobs
(
    gsl_vector* zt,        /*I */
    double ht,             /*I */
    gsl_matrix* tt,        /*I */
    gsl_matrix* rqr,     /*I */
    double* ft,         /*O*/
    gsl_matrix* pt,    /*I/O*/
    gsl_vector* kt,    /*I/O*/
    int m             /*I*/
);

/* diffuse filtering for missing obs */
void dfilter1step_missingobs
(
    gsl_vector* zt,        /*I */
    double ht,             /*I */
    gsl_matrix* tt,        /*I */
    gsl_matrix* rqr,     /*I */
    gsl_vector* at,    /*I/O: */
    double* ft,         /*O*/
    gsl_matrix* pt,    /*I/O*/
    gsl_vector* kt,    /*I/O*/
    double* finf,    /*I/O*/
    gsl_matrix* pinf,  /*I/O*/
    gsl_vector* kinf,  /*I/O*/
    int m,              /*I*/
    bool fast_mode
);



void filter1step_validobs
(
    float yt,             /*I */
    gsl_vector* zt,        /*I */
    float *ht,             /*I */
    gsl_matrix* tt,        /*I */
    gsl_matrix* rqr,     /*I */
    gsl_vector* at,    /*I/O*/
    gsl_matrix* pt,    /*I/O*/
    double* vt,     /*I/O*/
    double* ft,    /*I/O*/
    gsl_vector* kt,    /*I/O*/
    int m,
    gsl_vector* att
);



void filter1step_pred
(
    int pred_i,  /*I */
    gsl_vector* zt,        /*I */
    double ht,             /*I */
    gsl_matrix* tt,        /*I */
    gsl_matrix* rqr,     /*I */
    gsl_vector* at,    /*I: */
    double ft,
    gsl_matrix* pt,    /*I/O*/
    double* ft_records,    /*I/O: ft records */
    double** at_records,   /*I/O: at records */
    gsl_vector* kt,    /*I/O*/
    int m
);

void fit_cft2vec_a
(
     float *fit_cft,    /* I: harmonic coefficients  */
     gsl_vector* next_a,   /* I: state values    */
     int cur_date,      /* I: current date          */
     int m,             /* I: the number of states   */
     int structure     /*I: structure indicatore */
);

void vec_a2fit_cft
(
     gsl_vector *next_a,
     float *fit_cft,
     int cur_date,
     int m,
     int structure
);

float caculate_ini_p
(
    int m,
    gsl_vector* ini_a,
    gsl_vector* z
);

double compute_f
(
    gsl_matrix* P,
    ssmodel_constants instance
);


int initialize_ssmconstants
(
   int n_state,
   float rmse,
   double base_value,
   ssmodel_constants *instance
);
//typedef double optimfn(int n, double *par, void *ex);
//typedef void optimgr(int n, double *par, double *gr, void *ex);

//void vmmin(int n, double *x, double *Fmin, optimfn fn, optimgr gr, int maxit, int trace,
//int *mask, double abstol, double reltol, int nREPORT, void *ex, int *fncount, int *grcount, int *fail);
